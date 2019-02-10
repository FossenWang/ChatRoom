from django.test import TestCase
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async

from chat_server.routing import application
from utils import async_to_sync_function
from account.models import User

from .consumers import ChatConsumer


class ChatTestCase(TestCase):
    @async_to_sync_function
    async def test_chat(self):
        communicator_list = []
        users = await self.get_users()
        for user in users[:3]:
            session_cookie = await self.login_user(user)
            communicator = WebsocketCommunicator(
                application, "ws/chat/room/1/",
                headers=[(b'cookie', bytes(f'sessionid={session_cookie}', 'utf8'))])
            connected, _ = await communicator.connect()
            assert connected
            communicator_list.append(communicator)
            # test user & room info
            receive_data = await communicator.receive_json_from()
            self.assertEqual(receive_data['msg_type'], ChatConsumer.msg_types.USER_ROOM_INFO)
            communicator.user = receive_data['user']
            self.assertEqual(set(receive_data['user']), {'id', 'username', 'avatar'})
            self.assertEqual(set(receive_data['room']), {'id', 'name', 'onlineNumber', 'maxNumber'})

        await self.assertMessageNoError(communicator_list, 'test')
        await self.assertMessageNoError(communicator_list, 123)
        await self.assertMessageNoError(communicator_list, True)

        await self.assertMessageError(communicator_list[0], None)
        await self.assertMessageError(communicator_list[0], '   ')
        await self.assertMessageError(communicator_list[0], '\n\t')
        await self.assertMessageError(communicator_list[0], 'x' * 501)
        self._test_online_number(len(communicator_list))

        # test join & leave room msg
        session_cookie = await self.login_user(users[4])
        communicator_1 = WebsocketCommunicator(
            application, "ws/chat/room/1/",
            headers=[(b'cookie', bytes(f'sessionid={session_cookie}', 'utf8'))])
        connected, _ = await communicator_1.connect()
        assert connected
        receive_data = await communicator_1.receive_json_from()
        self.assertEqual(receive_data['msg_type'], ChatConsumer.msg_types.USER_ROOM_INFO)
        communicator_1.user = receive_data['user']
        # receive join msg
        for communicator in communicator_list:
            receive_data = await communicator.receive_json_from()
            self.assertEqual(receive_data['msg_type'], ChatConsumer.msg_types.JOIN_ROOM)
            self.assertDictEqual(receive_data['user'], communicator_1.user)
            self.assertEqual(receive_data['onlineNumber'], 4)

        # user login on other websocket
        session_cookie = await self.login_user(users[4])
        communicator_2 = WebsocketCommunicator(
            application, "ws/chat/room/1/",
            headers=[(b'cookie', bytes(f'sessionid={session_cookie}', 'utf8'))])
        connected, _ = await communicator_2.connect()
        assert connected
        receive_data = await communicator_2.receive_json_from()
        self.assertEqual(receive_data['msg_type'], ChatConsumer.msg_types.USER_ROOM_INFO)
        # the old channel was closed
        receive_data = await communicator_1.receive_output()
        assert receive_data['code'] == ChatConsumer.close_codes.OTHER_LOGIN

        # receive leave msg
        await communicator_2.disconnect()
        for communicator in communicator_list:
            receive_data = await communicator.receive_json_from()
            self.assertEqual(receive_data['msg_type'], ChatConsumer.msg_types.LEAVE_ROOM)
            self.assertDictEqual(receive_data['user'], communicator_1.user)
            self.assertEqual(receive_data['onlineNumber'], 3)

        # login required
        communicator = WebsocketCommunicator(application, "ws/chat/room/1/")
        connected, _ = await communicator.connect()
        assert connected
        receive_data = await communicator.receive_output()
        assert receive_data['code'] == ChatConsumer.close_codes.NOT_LOGIN

        # room dose not exist
        communicator = WebsocketCommunicator(
            application, "ws/chat/room/10/",
            headers=[(b'cookie', bytes(f'sessionid={session_cookie}', 'utf8'))])
        connected, _ = await communicator.connect()
        assert connected
        receive_data = await communicator.receive_output()
        assert receive_data['code'] == ChatConsumer.close_codes.ROOM_NOT_EXIST

        # room full
        for user in users[3:5]:
            session_cookie = await self.login_user(user)
            communicator = WebsocketCommunicator(
                application, "ws/chat/room/1/",
                headers=[(b'cookie', bytes(f'sessionid={session_cookie}', 'utf8'))])
            connected, _ = await communicator.connect()
            assert connected
            communicator_list.append(communicator)

        session_cookie = await self.login_user(users[5])
        communicator = WebsocketCommunicator(
            application, "ws/chat/room/1/",
            headers=[(b'cookie', bytes(f'sessionid={session_cookie}', 'utf8'))])
        connected, _ = await communicator.connect()
        assert connected
        receive_data = await communicator.receive_output()
        assert receive_data['code'] == ChatConsumer.close_codes.ROOM_FULL

        # close websockets
        for communicator in communicator_list:
            await communicator.disconnect()
        self._test_online_number(0)

    async def assertMessageNoError(self, communicator_list, message):
        # test send & receive message
        send_data = {'message': message}
        await communicator_list[0].send_json_to(send_data)
        for communicator in communicator_list:
            receive_data = None
            while not receive_data:
                receive_data = await communicator.receive_json_from()
                if receive_data['msg_type'] != ChatConsumer.msg_types.MESSAGE:
                    receive_data = None
            self.assertEqual(str(send_data['message']), receive_data['message'])
            self.assertDictEqual(receive_data['user'], communicator_list[0].user)

    async def assertMessageError(self, communicator, message):
        send_data = {'message': message}
        await communicator.send_json_to(send_data)
        receive_data = await communicator.receive_json_from()
        self.assertEqual(receive_data['msg_type'], ChatConsumer.msg_types.ERROR)
        self.assertIn('error', receive_data)

    def _test_online_number(self, online_number):
        c = self.client
        rsp = c.get('/api/chat/rooms/')
        self.assertEqual(rsp.status_code, 200)
        data = rsp.json()
        self.assertEqual(set(data['rooms'][0]), {'id', 'name', 'onlineNumber', 'maxNumber'})
        self.assertEqual(data['rooms'][0]['onlineNumber'], online_number)

    @database_sync_to_async
    def get_users(self):
        return list(User.objects.filter(is_superuser=False))

    async def login_user(self, user):
        is_login = await database_sync_to_async(self.client.login)(
            username=user.username, password='123456')
        assert is_login
        return self.client.cookies['sessionid'].value
