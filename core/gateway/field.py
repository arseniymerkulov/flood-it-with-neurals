from core.gateway.color import Color
from core.settings import Settings


settings = Settings.get_instance()


class Field:
    def __init__(self, size=settings.field_size):
        self.size = size
        self.data = [[Color.random() for j in range(size)] for i in range(size)]

    def get_data_to_num(self):
        return [[color.value for color in column] for column in self.data]

    def _get_starting_point_and_bias(self, turn_index: int):
        assert turn_index < 4

        def left_upper():
            return 0, 0, 1, 1

        def left_bottom():
            return 0, len(self.data) - 1, 1, -1

        def right_upper():
            return len(self.data) - 1, 0, -1, 1

        def right_bottom():
            return len(self.data) - 1, len(self.data) - 1, -1, -1

        return [left_upper, right_bottom, left_bottom, right_upper][turn_index]()

    def turn(self, turn_index: int, color: Color):
        sx, sy, bias_x, bias_y = self._get_starting_point_and_bias(turn_index)
        initial_color = self.data[sx][sy]
        corners = set()

        def update_field(starting_point):
            sx, sy = starting_point

            if self.data[sx][sy] == initial_color:
                self.data[sx][sy] = color

                if (sx == 0 or sx == self.size - 1) and (sy == 0 or sy == self.size - 1):
                    corners.add((sx, sy))

                new_x = sx + bias_x
                new_y = sy + bias_y

                if 0 <= new_x < self.size:
                    update_field((new_x, sy))

                if 0 <= new_y < self.size:
                    update_field((sx, new_y))

        update_field((sx, sy))
        corners.discard((sx, sy))
        killed = [i for i in range(4) if self._get_starting_point_and_bias(i)[0:2] in corners]
        colored = sum([len([node for node in column if node == color]) for column in self.data])

        return killed, colored, self.size ** 2
