from abc import ABC
from typing import Sequence, Generic

from exactly_lib.common.report_rendering.components import MajorBlockRenderer, MinorBlockRenderer, LineObjectRenderer, \
    SequenceRenderer, ELEMENT, Renderer, LineElementRenderer
from exactly_lib.common.report_rendering.trace_doc import TraceRenderer
from exactly_lib.util.simple_textstruct import structure
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock, Document, ElementProperties, \
    LineElement


class TraceDocRender(ABC):
    """Functionality to render itself as a :class:Document"""

    def render(self) -> Document:
        pass


def doc_of_single_major_block(block: MajorBlockRenderer) -> TraceDocRender:
    return DocumentFromSequence([block])


def doc_of_single_minor_block(block: MinorBlockRenderer) -> TraceDocRender:
    return doc_of_single_major_block(MajorBlockFromSequence([block]))


def doc_of_line_objects(line_elements: Sequence[LineElementRenderer]) -> TraceDocRender:
    return doc_of_single_minor_block(MinorBlockFromSequence(line_elements))


def doc_of_single_line_object(line_elements: Sequence[LineElementRenderer]) -> TraceDocRender:
    return doc_of_single_minor_block(MinorBlockFromSequence(line_elements))


class Concatenation(Generic[ELEMENT], SequenceRenderer[ELEMENT]):
    def __init__(self, elements: Sequence[Renderer[Sequence[ELEMENT]]]):
        self._elements = elements

    def render(self) -> Sequence[ELEMENT]:
        ret_val = []
        for element in self._elements:
            ret_val += element.render()

        return ret_val


class ASequence(Generic[ELEMENT], SequenceRenderer[ELEMENT]):
    """
    Renders a sequence.

    Special name of the class to avoid clash with builtin name.
    """

    def __init__(self, elements: Sequence[Renderer[ELEMENT]]):
        self._elements = elements

    def render(self) -> Sequence[ELEMENT]:
        return [
            element.render()
            for element in self._elements
        ]


class DocumentFromSequence(TraceDocRender):
    def __init__(self, blocks: Sequence[MajorBlockRenderer]):
        self._blocks = blocks

    def render(self) -> Document:
        return Document([
            block.render()
            for block in self._blocks
        ])


class DocumentFromTrace(TraceDocRender):
    def __init__(self, trace: TraceRenderer):
        self._trace = trace

    def render(self) -> Document:
        return Document(self._trace.render())


class MajorBlockFromSequence(MajorBlockRenderer):
    def __init__(self,
                 blocks: Sequence[MinorBlockRenderer],
                 properties: ElementProperties = structure.PLAIN_ELEMENT_PROPERTIES):
        self._properties = properties
        self._blocks = blocks

    def render(self) -> MajorBlock:
        return MajorBlock(
            [
                block.render()
                for block in self._blocks
            ],
            self._properties,
        )


class MinorBlockFromSequence(MinorBlockRenderer):
    def __init__(self,
                 line_elements: Sequence[LineElementRenderer],
                 properties: ElementProperties = structure.PLAIN_ELEMENT_PROPERTIES):
        self._properties = properties
        self._line_elements = line_elements

    def render(self) -> MinorBlock:
        return MinorBlock(
            [
                line_elements.render()
                for line_elements in self._line_elements
            ],
            self._properties,
        )


class LineElementFromLineObject(LineElementRenderer):
    def __init__(self,
                 line_object: LineObjectRenderer,
                 properties: ElementProperties = structure.PLAIN_ELEMENT_PROPERTIES):
        self.line_object = line_object
        self.properties = properties

    def render(self) -> LineElement:
        return LineElement(self.line_object.render(),
                           self.properties)
