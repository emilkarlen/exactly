from typing import Iterable

from exactly_lib.util.simple_textstruct.rendering import renderer_combinators as rend_comb
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer, SequenceRenderer


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
