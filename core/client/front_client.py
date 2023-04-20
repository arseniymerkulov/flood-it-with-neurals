import asyncio
import websockets


from core.utility.connection_type import ConnectionType
from core.utility.message_type import MessageType
from core.utility.message import (
    Message,
    MessageHandshake,
    MessageUpdateFieldResponse
)
from core.gateway.color import Color
from core.settings import Settings


settings = Settings.get_instance()


class Client:
    @staticmethod
    def run():
        async def handler():
            async with websockets.connect(settings.gateway_url) as socket:
                handshake = MessageHandshake(ConnectionType.front.value)
                await socket.send(Message.pack(handshake))\

                message = Message.unpack(await socket.recv())
                assert message.message_type == MessageType.init_field_request.value

                print('init field')
                print(message.data)

                while True:
                    message = Message.unpack(await socket.recv())
                    assert message.message_type == MessageType.update_field_request.value

                    print('update field')
                    print(message.data)

                    message = MessageUpdateFieldResponse()
                    await socket.send(Message.pack(message))

        asyncio.run(handler())


if __name__ == "__main__":
    Client.run()
