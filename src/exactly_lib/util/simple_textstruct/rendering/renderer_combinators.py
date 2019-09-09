from typing import Sequence, Generic, TypeVar

from exactly_lib.util.simple_textstruct.rendering.components import ELEMENT
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer, SequenceRenderer

T = TypeVar('T')


class ConstantR(Generic[T], Renderer[T]):
    def __init__(self, element: T):
        self._element = element

    def render(self) -> T:
        return self._element


class ConstantSequenceR(Generic[T], SequenceRenderer[T]):
    def __init__(self, elements: Sequence[T]):
        self._elements = elements

    def render_sequence(self) -> Sequence[T]:
        return self._elements


class ConcatenationR(Generic[ELEMENT], SequenceRenderer[ELEMENT]):
    def __init__(self, elements: Sequence[SequenceRenderer[ELEMENT]]):
        self._elements = elements

    def render_sequence(self) -> Sequence[ELEMENT]:
        ret_val = []
        for element in self._elements:
            ret_val += element.render_sequence()

        return ret_val


class PrependR(Generic[ELEMENT], SequenceRenderer[ELEMENT]):
    def __init__(self,
                 first: Renderer[ELEMENT],
                 following: SequenceRenderer[ELEMENT]):
        self._first = first
        self._following = following

    def render_sequence(self) -> Sequence[ELEMENT]:
        ret_val = [self._first.render()]
        ret_val += self._following.render_sequence()

        return ret_val


class AppendR(Generic[ELEMENT], SequenceRenderer[ELEMENT]):
    def __init__(self,
                 first: SequenceRenderer[ELEMENT],
                 last: Renderer[ELEMENT],
                 ):
        self._first = first
        self._last = last

    def render_sequence(self) -> Sequence[ELEMENT]:
        ret_val = list(self._first.render_sequence())
        ret_val.append(self._last.render())

        return ret_val


class SequenceR(Generic[ELEMENT], SequenceRenderer[ELEMENT]):
    """
    Renders a sequence.

    Special name of the class to avoid clash with builtin name.
    """

    def __init__(self, elements: Sequence[Renderer[ELEMENT]]):
        self._elements = elements

    def render_sequence(self) -> Sequence[ELEMENT]:
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

    def render_sequence(self) -> Sequence[ELEMENT]:
        return [
            self._element.render()
        ]
