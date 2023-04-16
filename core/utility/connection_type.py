import enum


class ConnectionType(enum.Enum):
    client = 'client'
    gateway = 'gateway'
    front = 'front'
