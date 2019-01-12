from django.core.exceptions import ObjectDoesNotExist
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from channels.exceptions import StopConsumer

from .models import Room


class RoomFull(Exception):
    pass


class RoomManager:
    def __init__(self):
        # rooms = {
        #     'name': '',
        #     'max_number': 10,
        #     'user_channels': {channel_name: user}
        # }
        self.active_rooms = {}
        self.channel_layer = get_channel_layer()

    def get_room_group_name(self, room_id):
        return f'chat_room{room_id}'

    async def get_room(self, room_id):
        if room_id in self.active_rooms:
            return self.active_rooms[room_id]

        room_object = await self.get_room_from_db(room_id)

        if room_id not in self.active_rooms:
            # 异步获取room期间，其他协程可能已更新self.active_rooms
            self.active_rooms[room_id] = {
                'name': room_object.name,
                'max_number': room_object.max_number,
                'user_channels': {},
            }
        return self.active_rooms[room_id]

    @database_sync_to_async
    def get_room_from_db(self, room_id):
        room_object = Room.objects.get(id=room_id)
        return room_object

    async def join_room(self, room_id, channel_name, user):
        # Join room group
        room = await self.get_room(room_id)

        if len(room['user_channels']) >= room['max_number']:
            raise RoomFull('Room is full')

        room['user_channels'][channel_name] = user
        await self.channel_layer.group_add(
            self.get_room_group_name(room_id),
            channel_name,
        )

    async def leave_room(self, room_id, channel_name):
        # Leave room group
        room = await self.get_room(room_id)
        del room['user_channels'][channel_name]
        if not room['user_channels']:
            del self.active_rooms[room_id]
        await self.channel_layer.group_discard(
            self.get_room_group_name(room_id),
            channel_name,
        )

    async def room_send(self, room_id, event):
        await self.channel_layer.group_send(
            self.get_room_group_name(room_id),
            event
        )

    def get_online_number(self, room_id):
        self._clean_active_room(room_id)
        room = self.active_rooms.get(room_id)
        if room:
            return len(room['user_channels'])
        return 0

    def get_online_users(self, room_id):
        self._clean_active_room(room_id)
        return self.active_rooms[room_id]['user_channels'].values()

    def _clean_active_room(self, room_id):
        room = self.active_rooms.get(room_id)
        if room:
            # 不同 backend 的 channel_layer 的 groups 获取方式不同
            # 此处仅为 InMemoryChannelLayer 的用法
            room_group_name = self.get_room_group_name(room_id)
            room_group = self.channel_layer.groups.get(room_group_name, {})

            for channel_name in list(room['user_channels'].keys()):
                if channel_name not in room_group:
                    del room['user_channels'][channel_name]
            if not room['user_channels']:
                del self.active_rooms[room_id]

room_manager = RoomManager()


class ChatConsumer(AsyncJsonWebsocketConsumer):
    class codes:
        ROOM_NOT_EXIST = 3000
        ROOM_FULL = 3001

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        user = self.scope['user']
        self.user = {
            'id': user.id,
            'is_anonymous': user.is_anonymous,
            'username': self.channel_name.replace('specific..inmemory!', '', 1),
        }
        try:
            await room_manager.join_room(self.room_id, self.channel_name, self.user)
            await self.accept()
        except ObjectDoesNotExist:
            await self.close(self.codes.ROOM_NOT_EXIST)
            raise StopConsumer()
        except RoomFull:
            await self.close(self.codes.ROOM_FULL)
            raise StopConsumer()

    async def disconnect(self, close_code):
        if close_code == self.codes.ROOM_NOT_EXIST:
            return
        try:
            await room_manager.leave_room(self.room_id, self.channel_name)
        except ObjectDoesNotExist:
            pass

    # Receive message from WebSocket
    async def receive_json(self, data):
        message = data['message']

        # Send message to room group
        await room_manager.room_send(self.room_id, {
            'type': 'chat_message',
            'message': message})

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send_json({'message': message})
