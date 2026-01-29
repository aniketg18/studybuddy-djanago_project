from django.db import models
from django.contrib.auth.models import User 
from django.contrib.auth import get_user_model
from django.conf import settings

# Create your models here.
class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    # Many-to-Many relationships
    skills_known = models.ManyToManyField(Skill, related_name="users_who_know", blank=True)
    skills_wanted = models.ManyToManyField(Skill, related_name="users_who_want", blank=True)

    def __str__(self):
        return self.user.username

class ConnectionRequest(models.Model):
    sender = models.ForeignKey(User, related_name="sent_requests", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_requests", on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("accepted", "Accepted"), ("rejected", "Rejected")],
        default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} → {self.receiver} ({self.status})"       
    
User = get_user_model()

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"
    
class Todo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todos')
    title = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {'Done' if self.completed else 'Pending'}"

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Note by {self.user.username} - {self.created_at.strftime('%Y-%m-%d')}"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username} : {self.content[:20]}"



class ChatMessage(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='chat_sent_messages',  # 👈 changed
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='chat_received_messages',  # 👈 changed
        on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender} -> {self.receiver}: {self.content[:20]}'

class ChatNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_notifications")  
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_chat_notifications")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} -> {self.user}: {self.message[:30]}"
