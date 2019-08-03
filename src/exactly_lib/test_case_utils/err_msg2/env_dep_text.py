from abc import ABC
from typing import TypeVar, Generic, Sequence

from exactly_lib.type_system.error_message import ErrorMessageResolvingEnvironment
from exactly_lib.util.simple_textstruct.rendering import renderer_combinators as rend_comb
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock

T = TypeVar('T')


class RendererResolver(Generic[T], ABC):
    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> Renderer[T]:
        pass


TextResolver = RendererResolver[Sequence[MajorBlock]]

ELEMENT = TypeVar('ELEMENT')


def sequence(elements: Sequence[RendererResolver[ELEMENT]]) -> RendererResolver[Sequence[ELEMENT]]:
    return _SequenceResolver(elements)


class _SequenceResolver(Generic[ELEMENT], RendererResolver[Sequence[ELEMENT]]):
    def __init__(self, element_resolvers: Sequence[RendererResolver[ELEMENT]]):
        self._element_resolvers = element_resolvers

    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> Renderer[Sequence[ELEMENT]]:
        return rend_comb.SequenceR(
            [
                element.resolve(environment)
                for element in self._element_resolvers
            ]
        )
