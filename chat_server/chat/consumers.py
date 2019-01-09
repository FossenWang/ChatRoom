from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer


class ChatRoom:
    rooms = {}
    max_rooms = 10
    channel_layer = get_channel_layer()

    def __new__(cls, room_name):
        if len(cls.rooms) >= cls.max_rooms:
            raise PermissionError(
                'The number of rooms has reached its maximum')
        room = super().__new__(cls)
        cls.rooms[room_name] = {'instance': room, 'channels': set()}
        return room

    def __init__(self, room_name):
        self.room_name = room_name

    @classmethod
    def get_room(cls, room_name):
        if room_name in cls.rooms:
            return cls.rooms[room_name]['instance']
        return None

    async def join_room(self, consumer):
        self.room_group_name = f'chat_{self.room_name}'
        self.rooms[self.room_name]['channels'].add(consumer.channel_name)

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            consumer.channel_name
        )

    async def leave_room(self, consumer):
        # Leave room group
        self.rooms[self.room_name]['channels'].discard(consumer.channel_name)
        await self.channel_layer.group_discard(
            self.room_group_name,
            consumer.channel_name
        )

    async def room_send(self, consumer, event):
        await self.channel_layer.group_send(
            self.room_group_name,
            event
        )

    @classmethod
    def _clean_room(cls):
        for room_name in cls.rooms:
            channels = cls.rooms[room_name]['channels']
            for channel_name in channels:
                if channel_name not in cls.channel_layer.channels:
                    channels.discard(channel_name)

ChatRoom('test')
rooms = [ChatRoom(f'room{i}') for i in range(9)]


def get_room(room_name):
    return ChatRoom.get_room(room_name)


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room = get_room(self.room_name)
        if not self.room:
            await self.close(3000)
            return
        await self.room.join_room(self)
        await self.accept()

    async def disconnect(self, close_code):
        if self.room:
            await self.room.leave_room(self)

    # Receive message from WebSocket
    async def receive_json(self, data):
        message = data['message']

        # Send message to room group
        await self.room.room_send(self, {
            'type': 'chat_message',
            'message': message})

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send_json({'message': message})
