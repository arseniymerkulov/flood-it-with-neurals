from core.gateway.color import Color
from core.settings import Settings


settings = Settings.get_instance()


class Field:
    def __init__(self, size=settings.field_size):
        self.size = size
        self.data = [[Color.random() for j in range(size)] for i in range(size)]

    def get_data_to_num(self):
        return [[color.value for color in column] for column in self.data]

    def get_starting_point(self, turn_index: int):
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

    def turn(self, turn_index: int, color: Color):
        sx, sy = self.get_starting_point(turn_index)
        initial_color = self.data[sx][sy]
        corners = set()

        def update_field(starting_point, marked):
            sx, sy = starting_point

            if sx < 0 or sx >= self.size or sy < 0 or sy >= self.size:
                return

            if marked[sx][sy] or self.data[sx][sy] != initial_color:
                return

            self.data[sx][sy] = color
            marked[sx][sy] = True

            if (sx == 0 or sx == self.size - 1) and (sy == 0 or sy == self.size - 1):
                corners.add((sx, sy))

            update_field((sx + 1, sy), marked)
            update_field((sx - 1, sy), marked)
            update_field((sx, sy + 1), marked)
            update_field((sx, sy - 1), marked)

        update_field((sx, sy), [[False for item in column] for column in self.data])
        corners.discard((sx, sy))
        killed = [i for i in range(4) if self.get_starting_point(i) in corners]

        marked = [[False for cell in row] for row in self.data]
        mask = [[0 for cell in row] for row in self.data]
        colored = self._search_field(color, (sx, sy), marked, mask)

        # return mask, killed, colored, colored == self.size ** 2
        return killed, colored, colored == self.size ** 2

    def get_colored_cells(self, turn_index):
        pass

    def get_initial_mask(self, turn_index):
        mask = [[0 for cell in row] for row in self.data]
        (sx, sy) = self.get_starting_point(turn_index)
        mask[sx][sy] = 1

        return mask

    def _search_field(self, initial_color, starting_point, marked, mask):
        sx, sy = starting_point

        if sx < 0 or sx >= self.size or sy < 0 or sy >= self.size:
            return 0

        if marked[sx][sy] or self.data[sx][sy] != initial_color:
            return 0

        if self.data[sx][sy] == initial_color:
            mask[sx][sy] = 1

        marked[sx][sy] = True

        return sum((1,
                    self._search_field(initial_color, (sx + 1, sy), marked, mask),
                    self._search_field(initial_color, (sx - 1, sy), marked, mask),
                    self._search_field(initial_color, (sx, sy + 1), marked, mask),
                    self._search_field(initial_color, (sx, sy - 1), marked, mask)))
