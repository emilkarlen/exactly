from abc import ABC
from typing import Sequence, TypeVar, Generic

from exactly_lib.common.report_rendering.trace_doc import Renderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock, LineElement, LineObject

ELEMENT = TypeVar('ELEMENT')


class SequenceRenderer(Generic[ELEMENT], Renderer[Sequence[ELEMENT]], ABC):
    pass


class MajorBlockRenderer(Renderer[MajorBlock], ABC):
    def render(self) -> MajorBlock:
        pass


class MajorBlocksRenderer(SequenceRenderer[MajorBlock], ABC):
    def render(self) -> Sequence[MajorBlock]:
        pass


class MinorBlockRenderer(Renderer[MinorBlock], ABC):
    def render(self) -> MinorBlock:
        pass


class MinorBlocksRenderer(SequenceRenderer[MinorBlock], ABC):
    def render(self) -> Sequence[MinorBlock]:
        pass


class LineElementRenderer(Renderer[LineElement], ABC):
    def render(self) -> LineElement:
        pass


class LineObjectRenderer(Renderer[LineObject], ABC):
    def render(self) -> LineObject:
        pass


class LineObjectsRenderer(SequenceRenderer[LineElement], ABC):
    def render(self) -> Sequence[LineElement]:
        pass
