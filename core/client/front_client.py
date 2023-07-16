import asyncio
import websockets
import numpy as np


from core.utility.connection_type import ConnectionType
from core.utility.message_type import MessageType
from core.utility.message import (
    Message,
    MessageHandshake,
    MessageReadyResponse,
    MessageUpdateFieldResponse
)
from core.settings import Settings


settings = Settings.get_instance()


class Client:
    @staticmethod
    def run():
        async def handler():
            async with websockets.connect(settings.gateway_url) as socket:
                handshake = MessageHandshake(ConnectionType.front.value)
                await socket.send(Message.pack(handshake))

                message = Message.unpack(await socket.recv())
                assert message.message_type == MessageType.ready_request.value

                ready = MessageReadyResponse()
                await socket.send(Message.pack(ready))

                message = Message.unpack(await socket.recv())
                assert message.message_type == MessageType.init_field_request.value

                print('init field')
                print(message.data)

                while True:
                    message = Message.unpack(await socket.recv())

                    if message.message_type == MessageType.update_field_request.value:
                        print('update field')
                        print(np.array(message.data['field']))

                        message = MessageUpdateFieldResponse()
                        await socket.send(Message.pack(message))

        asyncio.run(handler())


if __name__ == "__main__":
    Client.run()
