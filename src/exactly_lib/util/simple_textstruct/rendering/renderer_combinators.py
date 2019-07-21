from typing import Sequence, Generic, TypeVar

from exactly_lib.util.simple_textstruct.rendering.components import SequenceRenderer, \
    ELEMENT
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer

T = TypeVar('T')


class ConstantR(Generic[T], Renderer[T]):
    def __init__(self, element: T):
        self._element = element

    def render(self) -> T:
        return self._element


class ConcatenationR(Generic[ELEMENT], SequenceRenderer[ELEMENT]):
    def __init__(self, elements: Sequence[Renderer[Sequence[ELEMENT]]]):
        self._elements = elements

    def render(self) -> Sequence[ELEMENT]:
        ret_val = []
        for element in self._elements:
            ret_val += element.render()

        return ret_val


class SequenceR(Generic[ELEMENT], SequenceRenderer[ELEMENT]):
    """
    Renders a sequence.

    Special name of the class to avoid clash with builtin name.
    """

    def __init__(self, elements: Sequence[Renderer[ELEMENT]]):
        self._elements = elements

    def render(self) -> Sequence[ELEMENT]:
        return [
            element.render()
            for element in self._elements
        ]


class SingletonSequenceR(Generic[ELEMENT], SequenceRenderer[ELEMENT]):
    """
    Renders a sequence.

    Special name of the class to avoid clash with builtin name.
    """

    def __init__(self, element: Renderer[ELEMENT]):
        self._element = element

    def render(self) -> Sequence[ELEMENT]:
        return [
            self._element.render()
        ]
