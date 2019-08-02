from abc import ABC
from typing import TypeVar, Generic, Sequence

from exactly_lib.type_system.error_message import ErrorMessageResolvingEnvironment
from exactly_lib.util.simple_textstruct.rendering import renderer_combinators as rend_comb
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer

T = TypeVar('T')


class TextResolver(Generic[T], ABC):
    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> Renderer[T]:
        pass


ELEMENT = TypeVar('ELEMENT')


def sequence(elements: Sequence[TextResolver[ELEMENT]]) -> TextResolver[Sequence[ELEMENT]]:
    return _TextSequenceResolver(elements)


class _TextSequenceResolver(Generic[ELEMENT], TextResolver[Sequence[ELEMENT]]):
    def __init__(self, element_resolvers: Sequence[TextResolver[ELEMENT]]):
        self._element_resolvers = element_resolvers

    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> Renderer[Sequence[ELEMENT]]:
        return rend_comb.SequenceR(
            [
                element.resolve(environment)
                for element in self._element_resolvers
            ]
        )
