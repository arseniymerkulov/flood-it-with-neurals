import enum
import random


class Color(enum.Enum):
    red = 0
    green = 1
    blue = 2
    orange = 3
    yellow = 4
    magenta = 5

    @staticmethod
    def min():
        return min([color.value for color in Color])

    @staticmethod
    def max():
        return max([color.value for color in Color])

    @staticmethod
    def random():
        colors = [color.value for color in Color]
        min_color = min(colors)
        max_color = max(colors)
        return Color(random.randint(min_color, max_color))

