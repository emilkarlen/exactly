from typing import Iterable, TypeVar, Callable

from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import Renderer, SequenceRenderer
from exactly_lib.util.strings import ToStringObject


class AsToStringObject:
    def __init__(self, renderer: Renderer[str]):
        self._renderer = renderer

    def __str__(self) -> str:
        return self._renderer.render()


class JoiningOfElementRenderers(Renderer[str]):
    def __init__(self,
                 elements: Iterable[Renderer[str]],
                 separator: Renderer[str] = rend_comb.ConstantR(''),
                 ):
        """
        :param separator: Result is undefined if rendition differs between invocations
        """
        self._elements = elements
        self._separator = separator

    def render(self) -> str:
        return self._separator.render().join([
            element.render()
            for element in self._elements
        ])


class JoiningOfElementsRenderer(Renderer[str]):
    def __init__(self,
                 elements: SequenceRenderer[str],
                 separator: Renderer[str] = rend_comb.ConstantR(''),
                 ):
        """
        :param separator: Result is undefined if rendition differs between invocations
        """
        self._elements = elements
        self._separator = separator

    def render(self) -> str:
        return self._separator.render().join(self._elements.render_sequence())


T = TypeVar('T')


class OfObjectAndRenderingFunction(Renderer[str]):
    def __init__(self,
                 x: T,
                 renderer: Callable[[T], str],
                 ):
        self._x = x
        self._renderer = renderer

    def render(self) -> str:
        return self._renderer(self._x)


def of_to_string_object(x: ToStringObject) -> Renderer[str]:
    return OfObjectAndRenderingFunction(x, str)
