import re

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
        #     'online_users': {channel_name: user}
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
                'id': room_object.id,
                'name': room_object.name,
                'max_number': room_object.max_number,
                'online_users': {},
            }
        return self.active_rooms[room_id]

    @database_sync_to_async
    def get_room_from_db(self, room_id):
        room_object = Room.objects.get(id=room_id)
        return room_object

    async def join_room(self, room_id, channel_name, user):
        # Join room group
        room = await self.get_room(room_id)

        if len(room['online_users']) >= room['max_number']:
            raise RoomFull('Room is full')

        room['online_users'][channel_name] = user
        await self.channel_layer.group_add(
            self.get_room_group_name(room_id),
            channel_name,
        )

    async def leave_room(self, room_id, channel_name):
        # Leave room group
        room = await self.get_room(room_id)
        del room['online_users'][channel_name]
        if not room['online_users']:
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
            return len(room['online_users'])
        return 0

    def get_online_users(self, room_id):
        self._clean_active_room(room_id)
        return self.active_rooms[room_id]['online_users'].values()

    def _clean_active_room(self, room_id):
        room = self.active_rooms.get(room_id)
        if room:
            # 不同 backend 的 channel_layer 的 groups 获取方式不同
            # 此处仅为 InMemoryChannelLayer 的用法
            room_group_name = self.get_room_group_name(room_id)
            room_group = self.channel_layer.groups.get(room_group_name, {})

            for channel_name in list(room['online_users'].keys()):
                if channel_name not in room_group:
                    del room['online_users'][channel_name]
            if not room['online_users']:
                del self.active_rooms[room_id]

room_manager = RoomManager()


class ChatConsumer(AsyncJsonWebsocketConsumer):
    class codes:
        ROOM_NOT_EXIST = 3000
        ROOM_FULL = 3001

    class msg_types:
        ERROR = 0
        MESSAGE = 1
        USER_ROOM_INFO = 2
        JOIN_ROOM = 3
        LEAVE_ROOM = 4

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        # set id to distinguish anonymous users
        user_id = self.channel_name.replace('specific..inmemory!', '', 1)
        self.user = {
            'id': user_id,
            'username': f'游客({user_id})',
        }
        try:
            await room_manager.join_room(self.room_id, self.channel_name, self.user)
            await self.accept()
            await self.send_user_room_info()
            await room_manager.room_send(self.room_id, {
                'type': 'join_room_msg',
                'user': self.user,
                'onlineNumber': room_manager.get_online_number(self.room_id),
            })
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
            await room_manager.room_send(self.room_id, {
                'type': 'leave_room_msg',
                'user': self.user,
                'onlineNumber': room_manager.get_online_number(self.room_id),
            })
        except ObjectDoesNotExist:
            pass

    # Receive message from WebSocket
    async def receive_json(self, data):
        message = data.get('message')
        try:
            self.validate_message(message)
            message = str(message)
        except Exception as e:
            # Wrong message will only be send to sender,
            # and won't be send to others
            await self.send_json({
                'msg_type': self.msg_types.ERROR,
                'message': message,
                'error': str(e)})
            return

        # Send message to room group
        await room_manager.room_send(self.room_id, {
            'type': 'chat_message',
            'message': message,
            'user': self.user})

    def validate_message(self, message):
        assert message, 'Message is empty'
        message = str(message)
        assert not re.match(r'^[\s\f\r\t\n]*$', message), 'Message is empty'
        assert len(message) <= 500, "Message's length can't be larger than 500"

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send_json({
            'msg_type': self.msg_types.MESSAGE,
            'message': event['message'],
            'user': event['user']})

    async def send_user_room_info(self):
        # Send current user info to WebSocket
        room = await room_manager.get_room(self.room_id)
        await self.send_json({
            'msg_type': self.msg_types.USER_ROOM_INFO,
            'user': self.user,
            'room': {
                'id': room['id'],
                'name': room['name'],
                'maxNumber': room['max_number'],
                'onlineNumber': len(room['online_users']),
            }
        })

    async def join_room_msg(self, event):
        await self.send_json({
            'msg_type': self.msg_types.JOIN_ROOM,
            'user': event['user'],
            'onlineNumber': event['onlineNumber']})

    async def leave_room_msg(self, event):
        await self.send_json({
            'msg_type': self.msg_types.LEAVE_ROOM,
            'user': event['user'],
            'onlineNumber': event['onlineNumber']})
