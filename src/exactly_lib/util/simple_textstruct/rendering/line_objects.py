from exactly_lib.util.simple_textstruct import structure
from exactly_lib.util.simple_textstruct.rendering.components import LineObjectRenderer
from exactly_lib.util.simple_textstruct.structure import LineObject
from exactly_lib.util.strings import ToStringObject


class PreFormattedString(LineObjectRenderer):
    def __init__(self,
                 x: ToStringObject,
                 string_is_line_ended: bool = False
                 ):
        """
        :param x: str is accessed via __str__
        """
        self._x = x
        self._string_is_line_ended = string_is_line_ended

    def render(self) -> LineObject:
        return structure.PreFormattedStringLineObject(str(self._x), self._string_is_line_ended)


class StringLineObject(LineObjectRenderer):
    def __init__(self, x: ToStringObject):
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
