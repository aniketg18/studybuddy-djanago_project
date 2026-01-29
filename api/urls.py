# api/urls.py
#python -m daphne -p 8000 studybuddy.asgi:application
from django.urls import path
from .views import SkillListCreateView, SkillRetrieveUpdateDestroyView
from .views import RegisterView, ProfileView
from . import views
from .views import ProfileListCreateView
from .views import ProfileRetrieveUpdateView
from .views import MatchStudyBuddyView
from .views import SendConnectionRequestView, RespondConnectionRequestView
from .views import MatchView
from .views import add_todo, toggle_todo, add_note


urlpatterns = [
    path('skills/', SkillListCreateView.as_view(), name='skill-list-create'),
    path('skills/<int:pk>/', SkillRetrieveUpdateDestroyView.as_view(), name='skill-detail'),
    path('profile/update/', ProfileRetrieveUpdateView.as_view(), name='profile-update'),
    path('profiles/match/', MatchStudyBuddyView.as_view(), name='match-study-buddy'),
    path('match/', MatchView.as_view(), name='match'),
    path('discover/', views.discover_view, name="discover"),
    path('connection/send/<int:receiver_id>/', SendConnectionRequestView.as_view(), name="send-connection"),
    path("profile/<int:user_id>/", views.view_user_profile, name="view_user_profile"),
    path('search/', views.search_profiles, name='search_profiles'),
    path("notifications/<int:notif_id>/read/", views.mark_notification_read, name="mark_notification_read"),
   # Todo URLs
    path('add-todo/', views.add_todo, name='add_todo'),
    path('toggle-todo/<int:todo_id>/', views.toggle_todo, name='toggle_todo'),
    path('delete-todo/<int:todo_id>/', views.delete_todo, name='delete_todo'),
    # Note URL
    path('add-note/', views.add_note, name='add_note'),
    path('delete-note/<int:note_id>/', views.delete_note, name='delete_note'),
    # Chat URLs
    path('chat/<int:friend_id>/', views.chat_with_friend, name='chat_with_friend'),

    path("notifications/", views.get_notifications, name="get_notifications"),
    path("notifications/<int:notif_id>/read/", views.mark_notification_read, name="mark_notification_read"),
    path("notifications/dummy/", views.notifications_dummy, name="notifications_dummy"),

    

    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profiles/', ProfileListCreateView.as_view(), name='profile-list-create'),
    path('send-request/<int:receiver_id>/', views.send_connection_request, name='send_request'),
    path('connection/send/<int:receiver_id>/', SendConnectionRequestView.as_view(), name="send-connection"),
    path("connection/respond/<int:request_id>/<str:action>/", views.respond_connection_request_view,name="respond_connection_request"),
    path("connections/", views.connection_requests_view, name="connection_requests"),
]
