from django.test import TestCase
from channels.testing import WebsocketCommunicator

from utils import async_to_sync_function
from chat_server.routing import application


class ChatTestCase(TestCase):
    @async_to_sync_function
    async def test_chat(self):
        try:
            communicator_list = []
            for _ in range(5):
                communicator = WebsocketCommunicator(application, "ws/chat/room/1/")
                connected, _ = await communicator.connect()
                assert connected
                communicator_list.append(communicator)

            communicator = communicator_list[0]
            send_data = {'message': 'test'}
            await communicator.send_json_to(send_data)
            for communicator in communicator_list:
                receive_data = await communicator.receive_json_from()
                self.assertDictEqual(send_data, receive_data)

            self._test_rooms_api(len(communicator_list))
        finally:
            for communicator in communicator_list:
                await communicator.disconnect()
        self._test_rooms_api(0)

    def _test_rooms_api(self, online_number):
        c = self.client
        rsp = c.get('/api/chat/rooms/')
        self.assertEqual(rsp.status_code, 200)
        data = rsp.json()
        self.assertEqual(set(data['rooms'][0]), {'id', 'name', 'onlineNumber'})
        self.assertEqual(data['rooms'][0]['onlineNumber'], online_number)
