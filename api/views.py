from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import generics, permissions
from .models import Skill
from .serializers import SkillSerializer, UserSerializer, RegisterSerializer
from django.http import JsonResponse, HttpResponseForbidden
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Profile
from .serializers import ProfileSerializer
from rest_framework.views import APIView
from .models import ConnectionRequest, Notification
from .serializers import ConnectionRequestSerializer
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_user_model
from django.utils.html import escape
from .forms import UserUpdateForm, ProfileForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q 
from django.views.decorators.http import require_POST
from .models import Todo, Note, Message
from .models import ChatMessage
from .models import ChatNotification
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
# -------------------------------
# Home endpoint (welcome message)
# -------------------------------
@login_required(login_url="/login/")
def home_page(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    todos = request.user.todos.all().order_by('-created_at')
    notes = request.user.notes.all().order_by('-updated_at')
    friends = ConnectionRequest.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user),
        status="accepted"
    )
    return render(request, 'home.html', {
        'notifications': notifications,
        'todos': todos,
        'notes': notes,
        'friends': friends
    })



def login_view(request):
    if request.method == "POST":
        identifier = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""
        User = get_user_model()

        # resolve identifier to a real username (try username, then email), case-insensitive
        username_to_auth = identifier
        try:
            u = User.objects.get(username__iexact=identifier)
            username_to_auth = u.username
        except User.DoesNotExist:
            try:
                u = User.objects.get(email__iexact=identifier)
                username_to_auth = u.username
            except User.DoesNotExist:
                pass

        user = authenticate(request, username=username_to_auth, password=password)
        if user is not None and user.is_active:
            login(request, user)
            next_url = request.GET.get("next") or "home"
            return redirect(next_url)
        else:
            messages.error(request, "Invalid credentials")
            # fall through to re-render form
    return render(request, "login.html")

def register_view(request):
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        email = (request.POST.get("email") or "").strip()
        password = request.POST.get("password") or ""
        confirm_password = request.POST.get("confirm_password") or ""

        if not username or not password:
            messages.error(request, "Username and password are required")
            return redirect("register")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username already taken")
            return redirect("register")

        if email and User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email already in use")
            return redirect("register")

        user = User.objects.create_user(username=username, email=email, password=password)
        # ensure the user has a Profile
        Profile.objects.get_or_create(user=user)

        login(request, user)
        return redirect("home")

    return render(request, "register.html")

def logout_view(request):
    logout(request)
    return redirect("login")


# -------------------------------
# Skill Endpoints
# -------------------------------
class SkillListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/skills/    -> list all skills (public)
    POST /api/skills/    -> create a skill (requires login/JWT)
    """
    queryset = Skill.objects.all().order_by('name')
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # public read, login required to write


class SkillRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/skills/<id>/ -> retrieve one skill (public)
    PUT    /api/skills/<id>/ -> update (requires login/JWT)
    PATCH  /api/skills/<id>/ -> partial update (requires login/JWT)
    DELETE /api/skills/<id>/ -> delete (requires login/JWT)
    """
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# -------------------------------
# Authentication Endpoints
# -------------------------------
class RegisterView(generics.CreateAPIView):
    """
    POST /api/register/ -> Register a new user
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]  # anyone can register


class ProfileView(generics.RetrieveAPIView):
    """
    GET /api/profile/ -> Get details of the current logged-in user
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

# List all profiles / Create a new profile
class ProfileListCreateView(generics.ListCreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        skill_name = self.request.query_params.get('skill')  # ?skill=Python
        if skill_name:
            queryset = queryset.filter(skills_known__name__iexact=skill_name)
        return queryset

class ProfileRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Ensure users can only update their own profile
        return Profile.objects.get(user=self.request.user)         

class MatchStudyBuddyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_profile = request.user.profile  

        # Start with skill-based matching
        matched_profiles = Profile.objects.filter(
            skills_known__in=user_profile.skills_wanted.all()
        ).exclude(user=request.user).distinct()

        # Optional: filter by location if user has set one
        if user_profile.location:
            matched_profiles = matched_profiles.filter(location=user_profile.location)

        serializer = ProfileSerializer(matched_profiles, many=True)
        return Response(serializer.data)
      

# inside views.py -  SendConnectionRequestView.post method with this:
class SendConnectionRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, receiver_id):
        sender = request.user
        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response({"error": "Receiver not found"}, status=404)

        # Prevent sending request to self
        if sender == receiver:
            return Response({"error": "You cannot send a request to yourself"}, status=400)

        # Prevent sending if already accepted (friends)
        already_friends = ConnectionRequest.objects.filter(
            (Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender)),
            status="accepted"
        ).exists()
        if already_friends:
            return Response({"error": "Already friends"}, status=400)

        # Prevent duplicate pending requests from the same sender->receiver
        if ConnectionRequest.objects.filter(sender=sender, receiver=receiver, status="pending").exists():
            return Response({"error": "Request already sent"}, status=400)

        connection = ConnectionRequest.objects.create(sender=sender, receiver=receiver)
        serializer = ConnectionRequestSerializer(connection)
        return Response(serializer.data, status=201)


class RespondConnectionRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, request_id):
        try:
            connection = ConnectionRequest.objects.get(id=request_id, receiver=request.user)
        except ConnectionRequest.DoesNotExist:
            return Response({"error": "Request not found"}, status=404)

        action = request.data.get("action")  # "accept" or "reject"
        if action == "accept":
            connection.status = "accepted"
        elif action == "reject":
            connection.status = "rejected"
        else:
            return Response({"error": "Invalid action"}, status=400)

        connection.save()
        serializer = ConnectionRequestSerializer(connection)
        return Response(serializer.data)     


##############################
# inside views.py - replace send_connection_request function with this:
@login_required
@csrf_exempt
def send_connection_request(request, receiver_id):   # must accept receiver_id
    if request.method == "POST":
        try:
            receiver = User.objects.get(id=receiver_id)

            # prevent sending to yourself
            if request.user == receiver:
                return JsonResponse({"success": False, "message": "You cannot send request to yourself."})

            # check if already friends (accepted)
            if ConnectionRequest.objects.filter(
                (Q(sender=request.user, receiver=receiver) | Q(sender=receiver, receiver=request.user)),
                status="accepted"
            ).exists():
                return JsonResponse({"success": False, "message": "Already friends."})

            # prevent duplicate pending requests
            if ConnectionRequest.objects.filter(sender=request.user, receiver=receiver, status="pending").exists():
                return JsonResponse({"success": False, "message": "Friend request already sent."})

            ConnectionRequest.objects.create(sender=request.user, receiver=receiver)
            return JsonResponse({"success": True, "message": "Friend request sent!"})

        except User.DoesNotExist:
            return JsonResponse({"success": False, "message": "Receiver not found."})
    return JsonResponse({"success": False, "message": "Invalid request method."}, status=400)

     
@login_required
def connection_requests_view(request):
    received_requests = ConnectionRequest.objects.filter(receiver=request.user, status="pending")
    sent_requests = ConnectionRequest.objects.filter(sender=request.user)
    friends = ConnectionRequest.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user),
        status="accepted"
    )

    return render(request, "connection_requests.html", {
        "received_requests": received_requests,
        "sent_requests": sent_requests,
        "friends": friends,
        "user": request.user,  # for template comparison
    })

User = get_user_model()


def respond_connection_request_view(request, request_id, action):
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "message": "Authentication required"}, status=401)
        return redirect('login')

    conn = get_object_or_404(ConnectionRequest, id=request_id)

    if conn.receiver != request.user:
        return HttpResponseForbidden("You cannot respond to this request.")

    try:
        status_field = ConnectionRequest._meta.get_field('status')
        choices = [c[0] for c in status_field.choices]
    except Exception:
        choices = []

    if 'friends' in choices:
        accepted_value = 'friends'
    elif 'accepted' in choices:
        accepted_value = 'accepted'
    else:
        accepted_value = 'accepted'

    if action.lower() == "accept":
        conn.status = accepted_value
        conn.save()

        # save notification in DB
        notif = Notification.objects.create(
            user=conn.sender,
            message=f"{request.user.username} accepted your connection request."
        )

        # 🔔 also trigger WebSocket event in sender's group
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notifications_{conn.sender.id}",
            {
                "type": "notify",
                "data": {
                    "id": notif.id,
                    "sender": request.user.username,
                    "message": f"{request.user.username} accepted your connection request."
                }
            }
        )

        messages.success(request, "Connection accepted.")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"success": True, "message": "Accepted"})
        return redirect('connection_requests')

    elif action.lower() == "reject":
        conn.status = 'rejected' if 'rejected' in choices else 'rejected'
        conn.save()
        messages.success(request, "Request rejected.")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"success": True, "message": "Rejected"})
        return redirect('connection_requests')

    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "message": "Unknown action"}, status=400)
        messages.error(request, "Unknown action.")
        return redirect('connection_requests')


@login_required
def view_user_profile(request, user_id):
    """
    Show another user's profile before accepting a connection.
    """
    other_user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=other_user)

    # Check if current user and other_user are already friends
    connection = ConnectionRequest.objects.filter(
        (Q(sender=request.user, receiver=other_user) | Q(sender=other_user, receiver=request.user)),
        status="accepted"
    ).first()

    is_friend = connection is not None

    return render(request, "view_profile.html", {
        "other_user": other_user,
        "profile": profile,
        "is_friend": is_friend,
    })



####################################
class MatchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_profile = request.user.profile  

        # Skills the user knows and wants
        skills_known = user_profile.skills_known.all()
        skills_wanted = user_profile.skills_wanted.all()

        # Find matching profiles
        matches = Profile.objects.filter(
            skills_known__in=skills_wanted,   # They know what I want
            skills_wanted__in=skills_known    # They want what I know
        ).exclude(id=user_profile.id).distinct()  # Exclude myself

        serializer = ProfileSerializer(matches, many=True)
        return Response(serializer.data)    
    
@api_view(['POST'])
@permission_classes([AllowAny])  # anyone can register
def api_register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def api_home(request):
    return Response({"message": f"Welcome {request.user.username}, you are authenticated!"})


@login_required(login_url="/login/")
def profile_view(request):
    profile = request.user.profile
    return render(request, "profile.html", {"profile": profile})


@login_required
def edit_profile_view(request):
    user = request.user  

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")

        # update fields
        user.username = username
        user.email = email
        user.save()

        messages.success(request, "Profile updated successfully ✅")
        return redirect("edit_profile")

    return render(request, "edit_profile.html", {"user": user})

@login_required
def change_password_view(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # keep user logged in
            messages.success(request, "Password changed successfully ✅")
            return redirect("edit_profile")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "change_password.html", {"form": form})


@login_required
def edit_profile_view(request):
    user = request.user
    profile = user.profile  # OneToOne

    if request.method == "POST":
        # User fields
        user.username = request.POST.get("username") or user.username
        user.email = request.POST.get("email") or user.email
        user.save()

        # Profile fields
        profile.bio = request.POST.get("bio") or ""
        profile.location = request.POST.get("location") or ""
        profile.save()

        # Handle Skills (comma separated text)
        skills_known_text = request.POST.get("skills_known_text", "")
        skills_wanted_text = request.POST.get("skills_wanted_text", "")

        # Update Skills Known
        profile.skills_known.clear()
        for skill_name in [s.strip() for s in skills_known_text.split(",") if s.strip()]:
            skill, created = Skill.objects.get_or_create(name=skill_name)
            profile.skills_known.add(skill)

        # Update Skills Wanted
        profile.skills_wanted.clear()
        for skill_name in [s.strip() for s in skills_wanted_text.split(",") if s.strip()]:
            skill, created = Skill.objects.get_or_create(name=skill_name)
            profile.skills_wanted.add(skill)

        messages.success(request, "Profile updated successfully ✅")
        return redirect("profile")  # go back to profile page

    return render(request, "edit_profile.html", {
        "user": user,
        "profile": profile,
    })

@login_required
def profile_view(request):
    user = request.user
    profile = user.profile  # fetch the profile linked to this user

    return render(request, "profile.html", {
        "user": user,
        "profile": profile,
    })


@login_required
def discover_view(request):
    profiles_qs = Profile.objects.exclude(user=request.user)  # exclude myself

    # filtering logic
    skill = request.GET.get("skill")
    location = request.GET.get("location")
    if skill:
        profiles_qs = profiles_qs.filter(skills_known__name__icontains=skill)
    if location:
        profiles_qs = profiles_qs.filter(location__icontains=location)

    # Evaluate queryset to a list so we can attach attributes
    profiles = list(profiles_qs.distinct())

    # Attach request_status on each profile
    for p in profiles:
        # find latest connection request between current user and this profile user (if any)
        conn = ConnectionRequest.objects.filter(
            (Q(sender=request.user, receiver=p.user) | Q(sender=p.user, receiver=request.user))
        ).order_by('-created_at').first()

        if conn:
            # Normalize accepted value (your code uses 'accepted' in model choices)
            if conn.status == 'accepted' or conn.status == 'friends':
                p.request_status = 'friends'
            elif conn.status == 'pending':
                # determine direction
                if conn.sender_id == request.user.id:
                    p.request_status = 'pending'   # I sent -> pending
                else:
                    p.request_status = 'incoming'  # they sent -> incoming
            else:
                p.request_status = conn.status
        else:
            p.request_status = 'none'

    return render(request, "discover.html", {"profiles": profiles, "skill": skill, "location": location})



# api/views.py
from django.shortcuts import render
from .models import Profile

def search_profiles(request):
    skill_query = request.GET.get('skill', '').strip()
    location_query = request.GET.get('location', '').strip()

    profiles = Profile.objects.all()

    if skill_query:
        profiles = profiles.filter(skills__icontains=skill_query)

    if location_query:
        profiles = profiles.filter(location__icontains=location_query)

    context = {
        'profiles': profiles,
        'skill_query': skill_query,
        'location_query': location_query,
    }
    return render(request, 'search.html', context)

# -------------------------------
# Mark notification as read
# -------------------------------
@login_required
@require_POST
def mark_notification_read(request, notification_id):
    try:
        notif = Notification.objects.get(id=notification_id, user=request.user, is_read=False)
        notif.is_read = True
        notif.save()
        return JsonResponse({"success": True})
    except Notification.DoesNotExist:
        return JsonResponse({"success": False}, status=404)


############################################################################################################
#Todo
@login_required
def get_todos(request):
    todos = request.user.todos.all().order_by('-created_at')
    return render(request, 'todos.html', {'todos': todos})

@login_required
@require_POST
def add_todo(request):
    title = request.POST.get('title', '').strip()
    if title:
        todo = Todo.objects.create(user=request.user, title=title)
        # Return JSON for AJAX
        return JsonResponse({'id': todo.id, 'title': todo.title})
    return JsonResponse({'error': 'Title cannot be empty'}, status=400)

@login_required
@require_POST
def delete_todo(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id, user=request.user)
    todo.delete()
    return JsonResponse({'success': True})


@login_required
@require_POST
def toggle_todo(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id, user=request.user)
    todo.completed = not todo.completed
    todo.save()
    return JsonResponse({'success': True, 'completed': todo.completed})


#Notes
@login_required
def get_notes(request):
    notes = request.user.notes.all().order_by('-updated_at')
    return render(request, 'notes.html', {'notes': notes})

@login_required
@require_POST
def add_note(request):
    content = request.POST.get('content', '').strip()
    if content:
        note = Note.objects.create(user=request.user, content=content)
        return JsonResponse({'id': note.id, 'content': note.content})
    return JsonResponse({'error': 'Note cannot be empty'}, status=400)

@login_required
@require_POST
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.delete()
    return JsonResponse({'success': True})

#friends views 
@login_required
def friends_list(request):
    friends = ConnectionRequest.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user),
        status="accepted"
    )
    return render(request, 'friends_list.html', {'friends': friends})

#chat with friends
User = get_user_model()

@login_required
def chat_with_friend(request, friend_id):
    friend = get_object_or_404(User, id=friend_id)
    # fetch messages between the two users
    messages = ChatMessage.objects.filter(
        Q(sender=request.user, receiver=friend) | Q(sender=friend, receiver=request.user)
    ).order_by('timestamp')
    return render(request, 'chat.html', {'friend': friend, 'messages': messages})

############################################################################################################

@login_required
def get_notifications(request):
    notifications = ChatNotification.objects.filter(user=request.user, is_read=False)
    data = [
        {"id": n.id, "sender": n.sender.username, "message": n.message}
        for n in notifications
    ]
    return JsonResponse(data, safe=False)

@csrf_exempt
@login_required
def mark_notification_read(request, notif_id):
    try:
        notif = ChatNotification.objects.get(id=notif_id, user=request.user)
        notif.is_read = True
        notif.save()
        return JsonResponse({"status": "ok"})
    except ChatNotification.DoesNotExist:
        return JsonResponse({"status": "not found"}, status=404)
    
def notifications_dummy(request):
    return JsonResponse([], safe=False)   