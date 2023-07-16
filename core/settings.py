import logging
import torch


class Settings:
    logging.basicConfig(level=logging.INFO)
    _instance = None

    def __init__(self):
        self.gateway_url = 'ws://127.0.0.1:8080'
        self.field_size = 3

        # RL hyper parameters
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.save_path = 'models'
        self.batch_size = 32
        self.gamma = 0.99
        self.eps_start = 0.9
        self.eps_end = 0.05
        self.eps_decay = 1000
        self.tau = 0.005
        self.lr = 1e-4
        self.memory = 10000

    @staticmethod
    def get_instance():
        if not Settings._instance:
            Settings._instance = Settings()

        return Settings._instance
