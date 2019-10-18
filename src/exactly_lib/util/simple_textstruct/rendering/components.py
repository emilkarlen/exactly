from abc import ABC
from typing import TypeVar

from exactly_lib.util.render.renderer import Renderer, SequenceRenderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock, LineElement, LineObject, Document

ELEMENT = TypeVar('ELEMENT')


class DocumentRenderer(Renderer[Document], ABC):
    def render(self) -> Document:
        pass


class MajorBlockRenderer(Renderer[MajorBlock], ABC):
    pass


class MajorBlocksRenderer(SequenceRenderer[MajorBlock], ABC):
    pass


class MinorBlockRenderer(Renderer[MinorBlock], ABC):
    pass


class MinorBlocksRenderer(SequenceRenderer[MinorBlock], ABC):
    pass


class LineElementRenderer(Renderer[LineElement], ABC):
    pass


class LineObjectRenderer(Renderer[LineObject], ABC):
    pass


class LineObjectsRenderer(SequenceRenderer[LineObject], ABC):
    pass
