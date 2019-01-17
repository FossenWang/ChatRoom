from django.test import TestCase
from channels.testing import WebsocketCommunicator

from utils import async_to_sync_function
from chat_server.routing import application
from .consumers import ChatConsumer


class ChatTestCase(TestCase):
    @async_to_sync_function
    async def test_chat(self):
        communicator_list = []
        for _ in range(5):
            communicator = WebsocketCommunicator(application, "ws/chat/room/1/")
            connected, _ = await communicator.connect()
            assert connected
            communicator_list.append(communicator)
            # test user & room info
            receive_data = await communicator.receive_json_from()
            self.assertEqual(receive_data['msg_type'], ChatConsumer.msg_types.USER_ROOM_INFO)
            user = receive_data['user']
            communicator.user = user
            self.assertTrue(user['id'])
            self.assertEqual(user['username'], '')
            self.assertEqual(user['is_anonymous'], True)
            self.assertEqual(set(receive_data['room']), {'id', 'name', 'onlineNumber', 'maxNumber'})

        await self.assertMessageNoError(communicator_list, 'test')
        await self.assertMessageNoError(communicator_list, 123)
        await self.assertMessageNoError(communicator_list, True)

        await self.assertMessageError(communicator_list[0], None)
        await self.assertMessageError(communicator_list[0], '   ')
        await self.assertMessageError(communicator_list[0], '\n\t')
        await self.assertMessageError(communicator_list[0], 'x' * 501)
        self._test_online_number(len(communicator_list))

        # test join % leave room msg
        new_communicator = WebsocketCommunicator(application, "ws/chat/room/1/")
        connected, _ = await new_communicator.connect()
        assert connected
        receive_data = await new_communicator.receive_json_from()
        self.assertEqual(receive_data['msg_type'], ChatConsumer.msg_types.USER_ROOM_INFO)
        new_communicator.user = receive_data['user']
        # receive join msg
        for communicator in communicator_list:
            receive_data = await communicator.receive_json_from()
            self.assertEqual(receive_data['msg_type'], ChatConsumer.msg_types.JOIN_ROOM)
            self.assertDictEqual(receive_data['user'], new_communicator.user)
            self.assertEqual(receive_data['onlineNumber'], 6)

        await new_communicator.disconnect()
        # receive leave msg
        for communicator in communicator_list:
            receive_data = await communicator.receive_json_from()
            self.assertEqual(receive_data['msg_type'], ChatConsumer.msg_types.LEAVE_ROOM)
            self.assertDictEqual(receive_data['user'], new_communicator.user)
            self.assertEqual(receive_data['onlineNumber'], 5)

        # close websocket
        for communicator in communicator_list:
            await communicator.disconnect()

        self._test_online_number(0)

        # room dose not exist
        communicator = WebsocketCommunicator(application, "ws/chat/room/10/")
        connected, code = await communicator.connect()
        assert not connected and code == ChatConsumer.codes.ROOM_NOT_EXIST

        # room full
        communicator_list = []
        for _ in range(10):
            communicator = WebsocketCommunicator(application, "ws/chat/room/1/")
            connected, _ = await communicator.connect()
            assert connected
            communicator_list.append(communicator)

        communicator = WebsocketCommunicator(application, "ws/chat/room/1/")
        connected, code = await communicator.connect()
        assert not connected and code == ChatConsumer.codes.ROOM_FULL

        for communicator in communicator_list:
            await communicator.disconnect()

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
            self.assertEqual(send_data['message'], receive_data['message'])
            self.assertDictEqual(receive_data['user'], communicator_list[0].user)

    async def assertMessageError(self, communicator, message):
        send_data = {'message': message}
        await communicator.send_json_to(send_data)
        receive_data = await communicator.receive_json_from()
        self.assertEqual(receive_data['msg_type'], ChatConsumer.msg_types.ERROR)
        self.assertEqual(send_data['message'], receive_data['message'])
        self.assertIn('error', receive_data)

    def _test_online_number(self, online_number):
        c = self.client
        rsp = c.get('/api/chat/rooms/')
        self.assertEqual(rsp.status_code, 200)
        data = rsp.json()
        self.assertEqual(set(data['rooms'][0]), {'id', 'name', 'onlineNumber', 'maxNumber'})
        self.assertEqual(data['rooms'][0]['onlineNumber'], online_number)
