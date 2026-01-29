# api/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatMessage, ChatNotification

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.group_name = f'chat_{self.room_name}'

        if not self.scope["user"].is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get('message', '').strip()
        if not message_text:
            return

        sender = self.scope['user']
        try:
            a, b = self.room_name.split('_')
            uid1, uid2 = int(a), int(b)
        except Exception:
            return

        receiver_id = uid2 if sender.id == uid1 else uid1
        chat_msg = await self.save_message(sender.id, receiver_id, message_text)

        # also create and capture notification for receiver
        notif = await self.save_notification(sender.id, receiver_id, message_text)

        # broadcast chat message to chat group (unchanged)
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat.message',
                'message': message_text,
                'sender_id': sender.id,
                'timestamp': chat_msg.timestamp.isoformat()
            }
        )

        # send a real-time notification to the receiver's notification group (new)
        await self.channel_layer.group_send(
            f"notifications_{receiver_id}",
            {
                "type": "notify",   # will call NotificationConsumer.notify
                "data": {
                    "id": notif.id,                   # ChatNotification id (so mark as read can use it)
                    "sender": sender.username,
                    "message": message_text
                }
            }
        )

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, message_text):
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)
        return ChatMessage.objects.create(sender=sender, receiver=receiver, content=message_text)

    @database_sync_to_async
    def save_notification(self, sender_id, receiver_id, message_text):
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)
        return ChatNotification.objects.create(user=receiver, sender=sender, message=message_text)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'timestamp': event['timestamp']
        }))

# -----------------------
# New consumer: notifications (separate from chat)
# -----------------------
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope["user"].is_authenticated:
            await self.close()
            return

        url_user_id = int(self.scope["url_route"]["kwargs"]["user_id"])
        if url_user_id != self.scope["user"].id:
            await self.close()
            return

        self.user = self.scope["user"]
        self.group_name = f"notifications_{self.user.id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notify(self, event):
        """Handles 'notify' events sent by ChatConsumer"""
        data = event.get("data", {})
        await self.send(text_data=json.dumps(data))

