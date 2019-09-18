from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from exactly_lib.type_system.error_message import ErrorMessageResolvingEnvironment
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer, SequenceRenderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock

T = TypeVar('T')


class SequenceRendererResolver(Generic[T], ABC):
    @abstractmethod
    def resolve_sequence(self) -> SequenceRenderer[T]:
        pass


TextResolver = SequenceRendererResolver[MajorBlock]

ELEMENT = TypeVar('ELEMENT')
