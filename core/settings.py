import logging


class Settings:
    logging.basicConfig(level=logging.INFO)
    _instance = None

    def __init__(self):
        self.gateway_url = 'ws://192.168.0.2:8080'
        self.field_size = 3

    @staticmethod
    def get_instance():
        if not Settings._instance:
            Settings._instance = Settings()

        return Settings._instance
