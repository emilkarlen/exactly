from abc import ABC
from typing import Sequence

from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock, LineElement


class MajorBlockRenderer(ABC):
    def render(self) -> MajorBlock:
        pass


class MajorBlocksRenderer(ABC):
    def render(self) -> Sequence[MajorBlock]:
        pass


class MinorBlockRenderer(ABC):
    def render(self) -> MinorBlock:
        pass


class MinorBlocksRenderer(ABC):
    def render(self) -> Sequence[MinorBlock]:
        pass


class LineObjectRenderer(ABC):
    def render(self) -> LineElement:
        pass


class LineObjectsRenderer(ABC):
    def render(self) -> Sequence[LineElement]:
        pass
