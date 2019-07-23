from typing import Any

from exactly_lib.util.simple_textstruct import structure
from exactly_lib.util.simple_textstruct.rendering.components import LineObjectRenderer
from exactly_lib.util.simple_textstruct.structure import LineObject


class PreFormattedString(LineObjectRenderer):
    def __init__(self, x: Any):
        """
        :param x: str is accessed via __str__
        """
        self._x = x

    def render(self) -> LineObject:
        return structure.PreFormattedStringLineObject(str(self._x), False)


class StringLineObject(LineObjectRenderer):
    def __init__(self, x: Any):
        """
        :param x: str is accessed via __str__
        """
        self.x = x

    def render(self) -> LineObject:
        return structure.StringLineObject(str(self.x), False)


class HeaderLine(LineObjectRenderer):
    def __init__(self, line: str):
        self._line = line

    def render(self) -> LineObject:
        return structure.StringLineObject(
            self._line + ':',
            False,
        )
