from typing import Sequence

from exactly_lib.util.simple_textstruct import structure
from exactly_lib.util.simple_textstruct.rendering.components import MajorBlockRenderer, MinorBlockRenderer, \
    LineElementRenderer, DocumentRenderer
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock, Document, ElementProperties, \
    LineElement, LineObject


class DocumentR(DocumentRenderer):
    def __init__(self, contents: Renderer[Sequence[MajorBlock]]):
        self._contents = contents

    def render(self) -> Document:
        return Document(self._contents.render())


class MajorBlockR(MajorBlockRenderer):
    def __init__(self,
                 contents: Renderer[Sequence[MinorBlock]],
                 properties: ElementProperties = structure.PLAIN_ELEMENT_PROPERTIES):
        self._properties = properties
        self._contents = contents

    def render(self) -> MajorBlock:
        return MajorBlock(self._contents.render(),
                          self._properties,
                          )


class MinorBlockR(MinorBlockRenderer):
    def __init__(self,
                 contents: Renderer[Sequence[LineElement]],
                 properties: ElementProperties = structure.PLAIN_ELEMENT_PROPERTIES):
        self._properties = properties
        self._contents = contents

    def render(self) -> MinorBlock:
        return MinorBlock(
            self._contents.render(),
            self._properties,
        )


class LineElementR(LineElementRenderer):
    def __init__(self,
                 line_object: Renderer[LineObject],
                 properties: ElementProperties = structure.PLAIN_ELEMENT_PROPERTIES):
        self.line_object = line_object
        self.properties = properties

    def render(self) -> LineElement:
        return LineElement(self.line_object.render(),
                           self.properties)
