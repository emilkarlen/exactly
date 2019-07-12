from typing import Sequence

from exactly_lib.common.report_rendering.components import MajorBlocksRenderer, MajorBlockRenderer, \
    MinorBlocksRenderer, MinorBlockRenderer, LineObjectRenderer
from exactly_lib.test_case.result.trace_doc import TraceDocRender
from exactly_lib.util.simple_textstruct import structure
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock, Document, ElementProperties


def doc_of_single_major_block(block: MajorBlockRenderer) -> TraceDocRender:
    return DocumentFromSequence([block])


def doc_of_single_minor_block(block: MinorBlockRenderer) -> TraceDocRender:
    return doc_of_single_major_block(MajorBlockFromSequence([block]))


def doc_of_line_objects(line_objects: Sequence[LineObjectRenderer]) -> TraceDocRender:
    return doc_of_single_minor_block(MinorBlockFromSequence(line_objects))


def doc_of_single_line_object(line_object: LineObjectRenderer) -> TraceDocRender:
    return doc_of_single_minor_block(MinorBlockFromSequence([line_object]))


class DocumentFromSequence(TraceDocRender):
    def __init__(self, blocks: Sequence[MajorBlockRenderer]):
        self._blocks = blocks

    def render(self) -> Document:
        return Document([
            block.render()
            for block in self._blocks
        ])


class MajorBlocksFromSequence(MajorBlocksRenderer):
    def __init__(self, blocks: Sequence[MajorBlockRenderer]):
        self._blocks = blocks

    def render(self) -> Sequence[MajorBlock]:
        return [
            block.render()
            for block in self._blocks
        ]


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
                 line_objects: Sequence[LineObjectRenderer],
                 properties: ElementProperties = structure.PLAIN_ELEMENT_PROPERTIES):
        self._properties = properties
        self._line_objects = line_objects

    def render(self) -> MinorBlock:
        return MinorBlock(
            [
                line_object.render()
                for line_object in self._line_objects
            ],
            self._properties,
        )


class MinorBlocksFromSequence(MinorBlocksRenderer):
    def __init__(self, blocks: Sequence[MinorBlockRenderer]):
        self._blocks = blocks

    def render(self) -> Sequence[MinorBlock]:
        return [
            block.render()
            for block in self._blocks
        ]
