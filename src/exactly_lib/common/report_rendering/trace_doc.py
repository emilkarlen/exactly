from abc import ABC
from typing import Sequence, TypeVar, Generic

from exactly_lib.util.simple_textstruct.structure import MajorBlock

T = TypeVar('T')


class Renderer(Generic[T], ABC):
    def render(self) -> T:
        pass


TraceRenderer = Renderer[Sequence[MajorBlock]]
