from typing import Mapping, Any

from exactly_lib.util.simple_textstruct import structure
from exactly_lib.util.simple_textstruct.rendering.components import LineObjectRenderer
from exactly_lib.util.simple_textstruct.structure import LineObject


class PreFormattedString(LineObjectRenderer):
    def __init__(self, s: str):
        self._s = s

    def render(self) -> LineObject:
        return structure.PreFormattedStringLineObject(self._s, False)


class PreFormattedStringOfToString(LineObjectRenderer):
    def __init__(self, x: Any):
        self._x = x

    def render(self) -> LineObject:
        return structure.PreFormattedStringLineObject(
            str(self._x),
            False,
        )


class PreFormattedStringOfFormatString(LineObjectRenderer):
    def __init__(self, format_str: str, format_map: Mapping[str, Any]):
        self._format_str = format_str
        self._format_map = format_map

    def render(self) -> LineObject:
        return structure.PreFormattedStringLineObject(
            self._format_str.format_map(self._format_map),
            False,
        )


class PreFormattedStringOfFormatStringArgs(LineObjectRenderer):
    def __init__(self, format_str: str, args: tuple):
        self._format_str = format_str
        self._args = args

    def render(self) -> LineObject:
        return structure.PreFormattedStringLineObject(
            self._format_str.format(*self._args),
            False,
        )


class HeaderLine(LineObjectRenderer):
    def __init__(self, line: str):
        self._line = line

    def render(self) -> LineObject:
        return structure.StringLineObject(
            self._line + ':',
            False,
        )
