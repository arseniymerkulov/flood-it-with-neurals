import enum


class MessageType(enum.Enum):
    handshake = 'handshake'
    init_field_request = 'init_field_request'
    update_field_request = 'update_field_request'
    update_field_response = 'update_field_response'
    turn_request = 'turn_request'
    turn_response = 'turn_response'
    client_disconnected = 'client_disconnected'
