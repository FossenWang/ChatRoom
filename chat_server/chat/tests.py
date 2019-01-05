from django.test import TestCase
from channels.testing import WebsocketCommunicator

from tools import async_to_sync_function
from chat_server.routing import application


class ChatTestCase(TestCase):
    @async_to_sync_function
    async def test_chat(self):
        try:
            communicator_list = []
            for _ in range(5):
                communicator = WebsocketCommunicator(application, "ws/chat/test/")
                connected, _ = await communicator.connect()
                assert connected
                communicator_list.append(communicator)

            communicator = communicator_list[0]
            send_data = {'message': 'test'}
            await communicator.send_json_to(send_data)
            for communicator in communicator_list:
                receive_data = await communicator.receive_json_from()
                self.assertDictEqual(send_data, receive_data)
        finally:
            for communicator in communicator_list:
                await communicator.disconnect()
