import enum


class MessageType(enum.Enum):
    handshake = 'handshake'

    ready_request = 'ready_request'
    ready_response = 'ready_response'

    init_field_request = 'init_field_request'
    # TODO: init_field_response

    update_field_request = 'update_field_request'
    update_field_response = 'update_field_response'
    field_status_request = 'field_status_request'
    field_status_response = 'field_status_response'

    turn_request = 'turn_request'
    turn_response = 'turn_response'

    client_win = 'client_win'
    client_killed = 'client_killed'
    client_disconnected = 'client_disconnected'
