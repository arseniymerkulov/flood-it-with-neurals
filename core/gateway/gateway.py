from urllib.parse import urlparse
import asyncio
import websockets
import websockets.exceptions
import logging
import time


from core.utility.message_type import MessageType
from core.utility.message import (
    Message,
    MessageInitFieldRequest,
    MessageUpdateFieldRequest,
    MessageUpdateFieldResponse,
    MessageTurnRequest,
    MessageTurnResponse,
    MessageClientDisconnected
)
from core.utility.connection_type import ConnectionType
from core.gateway.field import Field
from core.gateway.color import Color
from core.settings import Settings


settings = Settings.get_instance()
logging.basicConfig(level=logging.INFO)


class Gateway:
    logger = logging.getLogger('Gateway')
    clients = set()
    front = set()

    @staticmethod
    def run():
        async def _send_update_field_request(socket, field, turn_index, color):
            message = MessageUpdateFieldRequest(field, turn_index, color)
            await socket.send(Message.pack(message))

            message = Message.unpack(await socket.recv())
            assert message.message_type == MessageType.update_field_response.value

            return message

        async def _send_turn_request(client):
            message = MessageTurnRequest()
            await client.send(Message.pack(message))

            message = Message.unpack(await client.recv())
            assert message.message_type == MessageType.turn_response.value

            return message

        async def handler(socket):
            message = await socket.recv()
            message = Message.unpack(message)

            assert message.message_type == MessageType.handshake.value

            if message.connection_type == ConnectionType.client.value:
                Gateway.logger.info(f'new client registered {socket}')
                Gateway.clients.add(socket)
                await asyncio.Future()

            elif message.connection_type == ConnectionType.front.value:
                if len(Gateway.front):
                    return

                Gateway.logger.info(f'new front registered {socket}')
                Gateway.front.add(socket)
                # mb make another client - BE

                # try:
                field = Field()
                message = MessageInitFieldRequest(field, len(Gateway.clients))
                await socket.send(Message.pack(message))

                Gateway.logger.info(f'send init field data')

                while True:
                    # remove discard inside for cycle
                    for i, client in enumerate(Gateway.clients):
                        try:
                            message = await _send_turn_request(client)

                        except websockets.exceptions.ConnectionClosedOK:
                            Gateway.clients.discard(client)

                            message = MessageClientDisconnected(i)
                            await socket.send(Message.pack(message))
                            continue

                        Gateway.logger.info(message.message_type)
                        color = message.data['color']
                        color = Color(int(color))
                        killed, colored, full = field.turn(i, color)
                        print(killed)
                        print(colored)
                        print(full)

                        await _send_update_field_request(socket, field, i, color)

                    # if killed
                    # discard killed from clients

                    time.sleep(2)
                # except websockets.exceptions.ConnectionClosedOK:
                #     Gateway.

        async def wrapper():
            scheme = urlparse(settings.gateway_url)

            async with websockets.serve(handler, scheme.hostname, scheme.port):
                await asyncio.Future()

        asyncio.run(wrapper())


if __name__ == '__main__':
    Gateway.run()
