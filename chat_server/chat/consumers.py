import re
from django.utils import timezone

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
        self.active_rooms = {}
        self.channel_layer = get_channel_layer()

    def get_room_group_name(self, room_id):
        return f'chat_room{room_id}'

    async def get_room(self, room_id):
        if room_id in self.active_rooms:
            return self.active_rooms[room_id]

        room_object = await self.get_room_from_db(room_id)

        if room_id not in self.active_rooms:
            # When get room from db asynchronously
            # other coroutines may populate the room
            self.active_rooms[room_id] = {
                'id': room_object.id,
                'name': room_object.name,
                'max_number': room_object.max_number,
                'online_users': {},
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

        if len(room['online_users']) >= room['max_number']:
            raise RoomFull('Room is full')

        user_id = user['id']

        # When user login on other websocket, force to close the old one
        user_already_in_room = False
        if user_id in room['user_channels']:
            user_already_in_room = True
            await self.channel_layer.group_discard(
                self.get_room_group_name(room_id),
                room['user_channels'][user_id],
            )
            await self.channel_layer.send(
                room['user_channels'][user_id],
                {'type': 'other_login', 'channel_name': channel_name}
            )

        room['online_users'][user_id] = user
        room['user_channels'][user_id] = channel_name
        await self.channel_layer.group_add(
            self.get_room_group_name(room_id),
            channel_name,
        )
        return user_already_in_room

    async def leave_room(self, room_id, user_id):
        # Leave room group
        room = await self.get_room(room_id)
        channel_name = room['user_channels'][user_id]
        await self.channel_layer.group_discard(
            self.get_room_group_name(room_id),
            channel_name,
        )
        del room['user_channels'][user_id]
        del room['online_users'][user_id]
        if not room['online_users']:
            del self.active_rooms[room_id]

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
            # "channel_layer.groups" is not common api,
            # can only be used in InMemoryChannelLayer
            room_group_name = self.get_room_group_name(room_id)
            room_group = self.channel_layer.groups.get(room_group_name, {})

            for key, channel_name in room['user_channels'].items():
                if channel_name not in room_group:
                    del room['user_channels'][key]
                    del room['online_users'][key]
            if not room['online_users']:
                del self.active_rooms[room_id]

room_manager = RoomManager()


class ChatConsumer(AsyncJsonWebsocketConsumer):
    class close_codes:
        ROOM_NOT_EXIST = 3000
        ROOM_FULL = 3001
        NOT_LOGIN = 3002
        OTHER_LOGIN = 3003

    class msg_types:
        ERROR = 0
        MESSAGE = 1
        USER_ROOM_INFO = 2
        JOIN_ROOM = 3
        LEAVE_ROOM = 4

    async def connect(self):
        # Accept first or no close code
        await self.accept()

        user_object = self.scope['user']
        if not user_object.is_authenticated:
            await self.close(self.close_codes.NOT_LOGIN)
            raise StopConsumer()

        try:
            self.room_id = self.scope['url_route']['kwargs']['room_id']
            self.user = {
                'id': user_object.id,
                'username': user_object.username,
                'avatar': user_object.avatar,
            }
            user_already_in_room = await room_manager.join_room(
                self.room_id, self.channel_name, self.user)
            await self.send_user_room_info()
            if user_already_in_room:
                return
            await room_manager.room_send(self.room_id, {
                'type': 'join_room_msg',
                'user': self.user,
                'onlineNumber': room_manager.get_online_number(self.room_id),
            })
        except ObjectDoesNotExist:
            await self.close(self.close_codes.ROOM_NOT_EXIST)
            raise StopConsumer()
        except RoomFull:
            await self.close(self.close_codes.ROOM_FULL)
            raise StopConsumer()

    async def disconnect(self, close_code):
        if close_code in (
                self.close_codes.ROOM_FULL,
                self.close_codes.ROOM_NOT_EXIST,
                self.close_codes.NOT_LOGIN,
                self.close_codes.OTHER_LOGIN):
            return

        try:
            await room_manager.leave_room(self.room_id, self.user['id'])
            await room_manager.room_send(self.room_id, {
                'type': 'leave_room_msg',
                'user': self.user,
                'onlineNumber': room_manager.get_online_number(self.room_id),
            })
        except ObjectDoesNotExist:
            pass

    async def receive(self, text_data=None, bytes_data=None):
        try:
            await super().receive(text_data, bytes_data)
        except Exception as e:
            # Wrong message will only be send to sender,
            # and won't be send to others
            await self.send_json({
                'msg_type': self.msg_types.ERROR,
                'error': str(e)})

    # Receive message from WebSocket
    async def receive_json(self, data):
        message = data.get('message')
        self.validate_message(message)
        message = str(message)

        # Send message to room group
        await room_manager.room_send(self.room_id, {
            'type': 'chat_message',
            'message': message,
            'time': timezone.now().timestamp(),
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
            'time': event['time'],
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
        if event['user']['id'] == self.user['id']:
            return
        await self.send_json({
            'msg_type': self.msg_types.JOIN_ROOM,
            'user': event['user'],
            'onlineNumber': event['onlineNumber']})

    async def leave_room_msg(self, event):
        await self.send_json({
            'msg_type': self.msg_types.LEAVE_ROOM,
            'user': event['user'],
            'onlineNumber': event['onlineNumber']})

    async def other_login(self, event):
        await self.close(self.close_codes.OTHER_LOGIN)
        raise StopConsumer()
