from core.gateway.color import Color
from core.settings import Settings


settings = Settings.get_instance()


class Field:
    def __init__(self, size=settings.field_size):
        self.size = size
        self.data = [[Color.random() for j in range(size)] for i in range(size)]

    def get_data_to_num(self):
        return [[color.value for color in column] for column in self.data]

    def _get_starting_point(self, turn_index: int):
        assert turn_index < 4

        def left_upper():
            return 0, 0

        def left_bottom():
            return 0, len(self.data) - 1

        def right_upper():
            return len(self.data) - 1, 0

        def right_bottom():
            return len(self.data) - 1, len(self.data) - 1

        return [left_upper, right_bottom, left_bottom, right_upper][turn_index]()

