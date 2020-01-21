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
    BRIGHT_RED = 91
    BRIGHT_GREEN = 92


class FontStyle(IntEnum):
    BOLD = 1
    ITALIC = 3
    UNDERLINE = 4


def ansi_escape(foreground: ForegroundColor, s: str) -> str:
    return '\033[1;' + str(int(foreground)) + 'm' + s + '\033[1;m'


def set_color(foreground: ForegroundColor) -> str:
    return '\033[1;' + str(int(foreground)) + 'm'


def set_font_style(style: FontStyle) -> str:
    return '\033[1;' + str(int(style)) + 'm'


def unset_color() -> str:
    return '\033[1;m'


def unset_font_style() -> str:
    return '\033[1;0m'


def is_file_object_with_color(file_object) -> bool:
    try:
        os.ttyname(file_object.fileno())
        return True
    except (AttributeError, OSError):
        return False
