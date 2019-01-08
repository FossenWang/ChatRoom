from channels.generic.websocket import AsyncJsonWebsocketConsumer


class ChatRoom:
    rooms = {}
    max_rooms = 10

    def __new__(cls, room_name):
        if len(cls.rooms) >= cls.max_rooms:
            raise PermissionError(
                'The number of rooms has reached its maximum')
        room = super().__new__(cls)
        cls.rooms[room_name] = room
        return room

    def __init__(self, room_name):
        self.room_name = room_name

    @classmethod
    def get_room(cls, room_name):
        return cls.rooms.get(room_name)

    async def join_room(self, consumer):
        self.room_group_name = f'chat_{self.room_name}'
        # Join room group
        await consumer.channel_layer.group_add(
            self.room_group_name,
            consumer.channel_name
        )

    async def leave_room(self, consumer):
        # Leave room group
        await consumer.channel_layer.group_discard(
            self.room_group_name,
            consumer.channel_name
        )

    async def room_send(self, consumer, event):
        await consumer.channel_layer.group_send(
            self.room_group_name,
            event
        )


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room = ChatRoom.rooms.get(self.room_name)
        if not self.room:
            self.room = ChatRoom(self.room_name)
        await self.room.join_room(self)
        await self.accept()

    async def disconnect(self, close_code):
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
