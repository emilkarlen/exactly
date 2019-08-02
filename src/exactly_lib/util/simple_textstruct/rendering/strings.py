from abc import ABC
from typing import Any, Mapping, Callable, TypeVar, Generic, Sequence


class StringConstructor(ABC):
    def __str__(self) -> str:
        pass


class Concatenate(StringConstructor):
    def __init__(self, elements: Sequence[Any]):
        """
        :param elements: List of elements that supports __str__
        """
        self._elements = elements

    def __str__(self) -> str:
        return ''.join([
            str(x)
            for x in self._elements
        ])


class FormatMap(StringConstructor):
    def __init__(self, format_str: str, format_map: Mapping[str, Any]):
        self._format_str = format_str
        self._format_map = format_map

    def __str__(self) -> str:
        return self._format_str.format_map(self._format_map)


class FormatPositional(StringConstructor):
    def __init__(self, format_str: str, *args):
        self._format_str = format_str
        self._args = args

    def __str__(self) -> str:
        return self._format_str.format(*self._args)


T = TypeVar('T')


class Transformed(Generic[T], StringConstructor):
    def __init__(self, x: T, transformer: Callable[[T], str]):
        self.x = x
        self._transformer = transformer

    def __str__(self) -> str:
        return self._transformer(self.x)
