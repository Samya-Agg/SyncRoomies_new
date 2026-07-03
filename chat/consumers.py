import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async

@sync_to_async
def get_last_50_messages(user1, user2):
    messages = Message.objects.filter(
        sender__username__in=[user1, user2],
        receiver__username__in=[user1, user2]
    ).order_by('timestamp')[:50]
    
    # Convert QuerySet to a list of dictionaries to avoid serialization issues
    return [
        {
            'message': msg.message,
            'sender': msg.sender.username,
            'timestamp': msg.timestamp.isoformat() if msg.timestamp else None
        }
        for msg in messages
    ]

@sync_to_async
def save_message(sender_username, receiver_username, message_text):
    sender = User.objects.get(username=sender_username)
    receiver = User.objects.get(username=receiver_username)
    message = Message.objects.create(
        sender=sender,
        receiver=receiver,
        message=message_text
    )
    return {
        'message': message.message,
        'sender': message.sender.username,
        'timestamp': message.timestamp.isoformat() if message.timestamp else None
    }

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user1 = self.scope['user'].username
        self.user2 = self.scope['url_route']['kwargs']['username']
        self.room_name = "_".join(sorted([self.user1, self.user2]))
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Load message history BUT flag it
        messages = await get_last_50_messages(self.user1, self.user2)
        for msg in messages:
            msg["history"] = True
            await self.send(text_data=json.dumps(msg))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "")

        # Save message
        message_data = await save_message(self.user1, self.user2, message)

        # ❗ Only broadcast through group_send
        # Do NOT send to sender manually!
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message_data
            }
        )


    async def chat_message(self, event):
        message_data = event['message']
        message_data["history"] = False
        await self.send(text_data=json.dumps(message_data))
