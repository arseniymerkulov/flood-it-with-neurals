import asyncio
import websockets
import logging


from core.utility.connection_type import ConnectionType
from core.utility.message_type import MessageType
from core.utility.message import (
    Message,
    MessageHandshake,
    MessageTurnResponse,
    MessageFieldStatusRequest
)
from core.gateway.color import Color
from core.gateway.field import Field
from core.client.ai.agent import Agent
from core.settings import Settings


settings = Settings.get_instance()
logging.basicConfig(level=logging.INFO)


class Client:
    logger = logging.getLogger('Client')

    @staticmethod
    def run():
        async def _game_session(socket, checkpoint=None):
            agent = Agent()

            if checkpoint:
                agent.load_model(checkpoint)

            old_state = {
                'field_size': None,
                'field': None,
                'colored': 1,
                'terminated': None
            }

            while True:
                message = Message.unpack(await socket.recv())
                assert message.message_type == MessageType.turn_request.value
                Client.logger.info('received turn request')

                message = MessageFieldStatusRequest()
                await socket.send(Message.pack(message))
                Client.logger.info('send field status request')

                message = Message.unpack(await socket.recv())
                assert message.message_type == MessageType.field_status_response.value

                old_state['field_size'] = message.data['field_size']
                old_state['field'] = message.data['field']
                old_state['terminated'] = message.data['terminated']

                action = agent.predict(old_state['field'])
                Client.logger.info(f'predict next action as {action}')

                message = MessageTurnResponse(Color(action))
                await socket.send(Message.pack(message))
                Client.logger.info(f'send turn response {message.data}')

                message = MessageFieldStatusRequest()
                await socket.send(Message.pack(message))
                Client.logger.info('send field status request')

                message = Message.unpack(await socket.recv())
                assert message.message_type == MessageType.field_status_response.value

                new_state = message.data
                reward = Agent.reward(old_state['colored'], new_state['colored'])
                agent.correct(old_state['field'],
                              new_state['field'],
                              action,
                              reward,
                              old_state['terminated'] or new_state['terminated'])

                import numpy as np
                print(np.array(old_state['field']))
                print(np.array(new_state['field']))
                print(reward)
                print('-------------------------------')

                old_state['colored'] = message.data['colored']

        async def handler():
            async with websockets.connect(settings.gateway_url) as socket:
                Client.logger.info(f'connection established with {settings.gateway_url}')

                handshake = MessageHandshake(ConnectionType.client.value)
                await socket.send(Message.pack(handshake))
                Client.logger.info('send handshake message')

                while True:
                    await _game_session(socket)

        asyncio.run(handler())


if __name__ == "__main__":
    Client.run()
