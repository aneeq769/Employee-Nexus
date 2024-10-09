import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message
from django.contrib.auth.models import User
from channels.db import database_sync_to_async

class EmployeesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope["user"].is_authenticated:
            await self.close()
            return

        self.user = self.scope["user"]
        self.group_name = f'user_{self.user.id}'

        # Join user-specific group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave user-specific group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        recipient_username = data.get('recipient_username')

        if not message or not recipient_username:
            await self.send(text_data=json.dumps({'error': 'Invalid message format'}))
            return

        try:
            recipient = await self.get_user_by_username(recipient_username)
        except User.DoesNotExist:
            await self.send(text_data=json.dumps({'error': 'Recipient does not exist'}))
            return

        # Save the message to the database
        new_message = await self.create_message(self.user, recipient, message)

        # Send message to recipient's group
        recipient_group = f'user_{recipient.id}'
        await self.channel_layer.group_send(
            recipient_group,
            {
                'type': 'chat_message',
                'sender_username': self.user.username,
                'recipient_username': recipient.username,
                'message': new_message.content,
                'timestamp': new_message.timestamp.isoformat()
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'sender': event['sender_username'],
            'recipient': event['recipient_username'],
            'message': event['message'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def get_user_by_username(self, username):
        return User.objects.get(username=username)

    @database_sync_to_async
    def create_message(self, sender, recipient, content):
        return Message.objects.create(sender=sender, recipient=recipient, content=content)
