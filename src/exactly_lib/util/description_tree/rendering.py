from typing import Sequence

from exactly_lib.util.ansi_terminal_color import ForegroundColor
from exactly_lib.util.description_tree.tree import Node, Detail, DetailVisitor, StringDetail, PreFormattedStringDetail
from exactly_lib.util.simple_textstruct import structure
from exactly_lib.util.simple_textstruct.rendering import renderer_combinators as rend_comb, elements
from exactly_lib.util.simple_textstruct.rendering.renderer import SequenceRenderer, Renderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock, LineElement, ElementProperties


class TreeRenderer(Renderer[MajorBlock]):
    def __init__(self, tree: Node[bool]):
        self._tree = tree

    def render(self) -> MajorBlock:
        return MajorBlock(_TreeRendererToMinorBlock(self._tree).render_sequence())


class _TreeRendererToMinorBlock(SequenceRenderer[MinorBlock]):
    def __init__(self, tree: Node[bool]):
        self._tree = tree

    def render_sequence(self) -> Sequence[MinorBlock]:
        return (
                [self._root()] +
                list(elements.IncreasedIndentRenderer(self._children_renderer()).render_sequence())
        )

    def _root(self) -> MinorBlock:
        return MinorBlock(
            [self._header_line()] +
            list(self._details_renderer().render_sequence())
        )

    def _header_line(self) -> LineElement:
        s = ' '.join([
            self._bool_header_string(),
            str(self._tree.header),
        ])

        return LineElement(
            structure.StringLineObject(s),
            _HEADER_PROPERTIES_FOR_T if self._tree.data else _HEADER_PROPERTIES_FOR_F,
        )

    def _children_renderer(self) -> SequenceRenderer[MinorBlock]:
        return rend_comb.ConcatenationR(
            [
                _TreeRendererToMinorBlock(child)
                for child in self._tree.children
            ]
        )

    def _details_renderer(self) -> SequenceRenderer[LineElement]:
        return rend_comb.ConcatenationR(
            [
                _DetailRendererToLineElements(detail)
                for detail in self._tree.details
            ]
        )

    def _bool_header_string(self) -> str:
        bool_char = 'T' if self._tree.data else 'F'

        return ''.join(['(', bool_char, ')'])


class _DetailRendererToLineElements(SequenceRenderer[LineElement],
                                    DetailVisitor[Sequence[LineElement]]):
    def __init__(self, detail: Detail):
        self._detail = detail

    def render_sequence(self) -> Sequence[LineElement]:
        return self._detail.accept(self)

    def visit_string(self, x: StringDetail) -> Sequence[LineElement]:
        return [
            LineElement(structure.StringLineObject(DETAILS_INDENT + str(x.string)))
        ]

    def visit_pre_formatted_string(self, x: PreFormattedStringDetail) -> Sequence[LineElement]:
        return [
            LineElement(structure.PreFormattedStringLineObject(str(x.object_with_to_string),
                                                               x.string_is_line_ended))
        ]


# Makes details appear 2 characters to the right of the node header
DETAILS_INDENT = '      '

_HEADER_PROPERTIES_FOR_F = ElementProperties(0, ForegroundColor.BRIGHT_RED, None)
_HEADER_PROPERTIES_FOR_T = ElementProperties(0, ForegroundColor.BRIGHT_GREEN, None)
