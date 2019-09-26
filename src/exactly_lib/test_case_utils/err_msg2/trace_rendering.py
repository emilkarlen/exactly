from typing import Sequence

from exactly_lib.type_system.trace.trace import Node, Detail, DetailVisitor, StringDetail, PreFormattedStringDetail
from exactly_lib.util.ansi_terminal_color import ForegroundColor
from exactly_lib.util.simple_textstruct import structure
from exactly_lib.util.simple_textstruct.rendering import renderer_combinators as rend_comb, elements
from exactly_lib.util.simple_textstruct.rendering.renderer import SequenceRenderer, Renderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock, LineElement, ElementProperties


class BoolTraceRenderer(Renderer[MajorBlock]):
    def __init__(self, trace: Node[bool]):
        self._trace = trace

    def render(self) -> MajorBlock:
        return MajorBlock(_NodeRendererToMinorBlock(self._trace).render_sequence())


class _NodeRendererToMinorBlock(SequenceRenderer[MinorBlock]):
    def __init__(self, node: Node[bool]):
        self._node = node

    def render_sequence(self) -> Sequence[MinorBlock]:
        return (
                [self._root()] +
                list(elements.IncreasedIndentRenderer(self._children_renderer()).render_sequence())
        )

    def _root(self) -> MinorBlock:
        return MinorBlock(
            [self._header_line()] +
            list(elements.IncreasedIndentRenderer(self._details_renderer()).render_sequence())
        )

    def _header_line(self) -> LineElement:
        s = ' '.join([self._node.header, self._bool_header_tail()])

        return LineElement(
            structure.StringLineObject(s),
            _HEADER_PROPERTIES_FOR_T if self._node.data else _HEADER_PROPERTIES_FOR_F,
        )

    def _children_renderer(self) -> SequenceRenderer[MinorBlock]:
        return rend_comb.ConcatenationR(
            [
                _NodeRendererToMinorBlock(child)
                for child in self._node.children
            ]
        )

    def _details_renderer(self) -> SequenceRenderer[LineElement]:
        return rend_comb.ConcatenationR(
            [
                _DetailRendererToLineElements(detail)
                for detail in self._node.details
            ]
        )

    def _bool_header_tail(self) -> str:
        bool_char = 'T' if self._node.data else 'F'

        return ''.join(['(', bool_char, ')'])


class _DetailRendererToLineElements(SequenceRenderer[LineElement],
                                    DetailVisitor[Sequence[LineElement]]):
    def __init__(self, detail: Detail):
        self._detail = detail

    def render_sequence(self) -> Sequence[LineElement]:
        return self._detail.accept(self)

    def visit_string(self, x: StringDetail) -> Sequence[LineElement]:
        return [
            LineElement(structure.StringLineObject(x.string))
        ]

    def visit_pre_formatted_string(self, x: PreFormattedStringDetail) -> Sequence[LineElement]:
        return [
            LineElement(structure.PreFormattedStringLineObject(x.object_with_to_string,
                                                               x.string_is_line_ended))
        ]


_HEADER_PROPERTIES_FOR_F = ElementProperties(0, ForegroundColor.RED, None)
_HEADER_PROPERTIES_FOR_T = ElementProperties(0, ForegroundColor.GREEN, None)
