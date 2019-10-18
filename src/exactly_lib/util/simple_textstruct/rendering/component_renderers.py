from exactly_lib.util.render.renderer import Renderer, SequenceRenderer
from exactly_lib.util.simple_textstruct import structure
from exactly_lib.util.simple_textstruct.rendering.components import MajorBlockRenderer, MinorBlockRenderer, \
    LineElementRenderer, DocumentRenderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock, Document, ElementProperties, \
    LineElement, LineObject


class DocumentR(DocumentRenderer):
    def __init__(self, contents: SequenceRenderer[MajorBlock]):
        self._contents = contents

    def render(self) -> Document:
        return Document(self._contents.render_sequence())


class MajorBlockR(MajorBlockRenderer):
    def __init__(self,
                 contents: SequenceRenderer[MinorBlock],
                 properties: ElementProperties = structure.ELEMENT_PROPERTIES__NEUTRAL):
        self._properties = properties
        self._contents = contents

    def render(self) -> MajorBlock:
        return MajorBlock(self._contents.render_sequence(),
                          self._properties,
                          )


class MinorBlockR(MinorBlockRenderer):
    def __init__(self,
                 contents: SequenceRenderer[LineElement],
                 properties: ElementProperties = structure.ELEMENT_PROPERTIES__NEUTRAL):
        self._properties = properties
        self._contents = contents

    def render(self) -> MinorBlock:
        return MinorBlock(
            self._contents.render_sequence(),
            self._properties,
        )


class LineElementR(LineElementRenderer):
    def __init__(self,
                 line_object: Renderer[LineObject],
                 properties: ElementProperties = structure.ELEMENT_PROPERTIES__NEUTRAL):
        self.line_object = line_object
        self.properties = properties

    def render(self) -> LineElement:
        return LineElement(self.line_object.render(),
                           self.properties)
