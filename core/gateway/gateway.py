from urllib.parse import urlparse
import asyncio
import websockets
import websockets.exceptions
import logging
import time


from core.utility.message_type import MessageType
from core.utility.message import (
    Message,
    MessageReadyRequest,
    MessageInitFieldRequest,
    MessageUpdateFieldRequest,
    MessageTurnRequest,
    MessageFieldStatusResponse,
    MessageClientWin,
    MessageClientKilled,
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

        async def _send_turn_request(client, field, colored, terminated):
            message = MessageTurnRequest()
            await client.send(Message.pack(message))

            message = Message.unpack(await client.recv())
            print(message)
            assert message.message_type == MessageType.field_status_request.value

            message = MessageFieldStatusResponse(field, colored, terminated)
            await client.send(Message.pack(message))

            message = Message.unpack(await client.recv())
            assert message.message_type == MessageType.turn_response.value

            return message

        async def _game_session(front):
            try:
                if not len(Gateway.clients):
                    return

                field = Field()
                message = MessageInitFieldRequest(field, len(Gateway.clients))
                await front.send(Message.pack(message))

                Gateway.logger.info(f'send init field data')

                while True:
                    disconnected = []
                    killed = []

                    for i, client in enumerate(Gateway.clients):
                        if i in killed:
                            continue

                        try:
                            message = await _send_turn_request(client, field, None, False)
                            Gateway.logger.info(f'get turn data from client {i}')

                        except websockets.exceptions.ConnectionClosedOK:
                            disconnected.append(client)
                            message = MessageClientDisconnected(i)
                            await front.send(Message.pack(message))
                            Gateway.logger.info(f'client {i} disconnect')
                            continue

                        Gateway.logger.info(message.message_type)
                        color = message.data['color']
                        color = Color(int(color))
                        kills, colored, win = field.turn(i, color)

                        try:
                            message = Message.unpack(await client.recv())
                            assert message.message_type == MessageType.field_status_request.value

                            message = MessageFieldStatusResponse(field, colored, False)
                            await client.send(Message.pack(message))

                            Gateway.logger.info(f'get turn data from client {i}')

                        except websockets.exceptions.ConnectionClosedOK:
                            disconnected.append(client)
                            message = MessageClientDisconnected(i)
                            await front.send(Message.pack(message))
                            Gateway.logger.info(f'client {i} disconnect')
                            continue

                        await _send_update_field_request(front, field, i, color)

                        for j in kills:
                            message = MessageClientKilled(j)
                            await front.send(Message.pack(message))
                            killed.append(j)
                            Gateway.logger.info(f'client {j} killed')

                        if win:
                            message = MessageClientWin(i)
                            await front.send(Message.pack(message))
                            Gateway.logger.info(f'client {i} win')
                            return

                    [Gateway.clients.discard(client) for client in disconnected]
                    if not len(Gateway.clients):
                        return
                    time.sleep(2)

            except websockets.exceptions.ConnectionClosedOK:
                Gateway.front = set()
                return

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

                while True:
                    message = MessageReadyRequest()
                    await socket.send(Message.pack(message))

                    message = await socket.recv()
                    message = Message.unpack(message)
                    assert message.message_type == MessageType.ready_response.value
                    await _game_session(socket)

        async def wrapper():
            scheme = urlparse(settings.gateway_url)

            async with websockets.serve(handler, scheme.hostname, scheme.port):
                await asyncio.Future()

        asyncio.run(wrapper())


if __name__ == '__main__':
    Gateway.run()
