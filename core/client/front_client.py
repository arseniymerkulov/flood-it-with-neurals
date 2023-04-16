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
                await socket.send(Message.pack(handshake))

                while True:
                    message = Message.unpack(await socket.recv())
                    print(message.message_type)
                    print(MessageType.update_field_request.value)
                    assert message.message_type == MessageType.update_field_request.value

                    print(message.data)

                    message = MessageUpdateFieldResponse()
                    await socket.send(Message.pack(message))

        asyncio.run(handler())


if __name__ == "__main__":
    Client.run()
