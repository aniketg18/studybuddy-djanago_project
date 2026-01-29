# api/routing.py
from django.urls import path
from . import consumers
from django.urls import re_path

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
    re_path(r"ws/notifications/(?P<user_id>\d+)/$", consumers.NotificationConsumer.as_asgi()),
]
