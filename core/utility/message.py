import json


from core.utility.connection_type import ConnectionType
from core.utility.message_type import MessageType
from core.gateway.field import Field
from core.gateway.color import Color


class Message:
    def __init__(self,
                 message_type: MessageType,
                 connection_type: ConnectionType,
                 data):
        self.message_type = message_type
        self.connection_type = connection_type
        self.data = data

    @staticmethod
    def pack(message):
        return json.dumps(message.__dict__)

    @staticmethod
    def unpack(message: str):
        json_data = json.loads(message)
        return Message(json_data['message_type'], json_data['connection_type'], json_data['data'])


class MessageHandshake(Message):
    def __init__(self, connection_type: ConnectionType):
        super().__init__(MessageType.handshake.value,
                         connection_type,
                         {})


class MessageReadyRequest(Message):
    def __init__(self):
        super().__init__(MessageType.ready_request.value,
                         ConnectionType.gateway.value,
                         {})


class MessageReadyResponse(Message):
    def __init__(self):
        super().__init__(MessageType.ready_response.value,
                         ConnectionType.front.value,
                         {})


class MessageInitFieldRequest(Message):
    def __init__(self, field: Field, players: int):
        data = {
            'field_size': field.size,
            'field': field.get_data_to_num(),
            'max_color': Color.max(),
            'players': players
        }

        super().__init__(MessageType.init_field_request.value,
                         ConnectionType.gateway.value,
                         data)


class MessageUpdateFieldRequest(Message):
    def __init__(self, field: Field, turn_index: int, color: Color):
        data = {
            'field_size': field.size,
            'field': field.get_data_to_num(),
            'color': color.value,
            'turn': turn_index,
        }

        super().__init__(MessageType.update_field_request.value,
                         ConnectionType.gateway.value,
                         data)


class MessageUpdateFieldResponse(Message):
    def __init__(self):
        super().__init__(MessageType.update_field_response.value,
                         ConnectionType.front.value,
                         {})


class MessageFieldStatusRequest(Message):
    def __init__(self):
        super().__init__(MessageType.field_status_request.value,
                         ConnectionType.client.value,
                         {})


class MessageFieldStatusResponse(Message):
    def __init__(self, field: Field, colored, terminated):
        super().__init__(MessageType.field_status_response.value,
                         ConnectionType.gateway.value,
                         {
                             'field_size': field.size,
                             'field': field.get_data_to_num(),
                             'colored': colored,
                             'terminated': terminated
                         })


class MessageTurnRequest(Message):
    def __init__(self):
        super().__init__(MessageType.turn_request.value,
                         ConnectionType.gateway.value,
                         {})


class MessageTurnResponse(Message):
    def __init__(self, color: Color):
        super().__init__(MessageType.turn_response.value,
                         ConnectionType.client.value,
                         {
                             'color': color.value
                         })


class MessageClientWin(Message):
    def __init__(self, turn_index: int):
        super().__init__(MessageType.client_win.value,
                         ConnectionType.gateway.value,
                         {
                             'turn': turn_index
                         })


class MessageClientKilled(Message):
    def __init__(self, turn_index: int):
        super().__init__(MessageType.client_killed.value,
                         ConnectionType.gateway.value,
                         {
                             'turn': turn_index
                         })


class MessageClientDisconnected(Message):
    def __init__(self, turn_index: int):
        super().__init__(MessageType.client_disconnected.value,
                         ConnectionType.gateway.value,
                         {
                             'turn': turn_index
                         })
