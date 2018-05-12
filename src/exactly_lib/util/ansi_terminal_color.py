import os
from enum import IntEnum


class ForegroundColor(IntEnum):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    PURPLE = 35
    CYAN = 36
    WHITE = 37


def ansi_escape(foreground: ForegroundColor, s: str) -> str:
    return '\033[1;' + str(int(foreground)) + 'm' + s + '\033[1;m'


def is_file_object_with_color(file_object) -> bool:
    try:
        os.ttyname(file_object.fileno())
        return True
    except OSError or AttributeError:
        return False
