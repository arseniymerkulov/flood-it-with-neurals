import asyncio
import websockets
import logging


from core.utility.connection_type import ConnectionType
from core.utility.message_type import MessageType
from core.utility.message import (
    Message,
    MessageHandshake,
    MessageTurnResponse
)
from core.gateway.color import Color
from core.settings import Settings


settings = Settings.get_instance()
logging.basicConfig(level=logging.INFO)


class Client:
    logger = logging.getLogger('Client')

    @staticmethod
    def run():
        async def handler():
            async with websockets.connect(settings.gateway_url) as socket:
                Client.logger.info(f'connection established with {settings.gateway_url}')

                handshake = MessageHandshake(ConnectionType.client.value)
                await socket.send(Message.pack(handshake))
                Client.logger.info('send handshake message')

                while True:
                    message = Message.unpack(await socket.recv())
                    assert message.message_type == MessageType.turn_request.value

                    Client.logger.info('received turn request')

                    message = MessageTurnResponse(Color.random())
                    await socket.send(Message.pack(message))
                    Client.logger.info(f'send turn response {message.data}')

        asyncio.run(handler())


if __name__ == "__main__":
    Client.run()
