from typing import Sequence, Generic, Callable

from exactly_lib.util.description_tree.tree import Node, Detail, DetailVisitor, StringDetail, PreFormattedStringDetail, \
    NODE_DATA
from exactly_lib.util.simple_textstruct import structure
from exactly_lib.util.simple_textstruct.rendering import renderer_combinators as rend_comb, elements
from exactly_lib.util.simple_textstruct.rendering.renderer import SequenceRenderer, Renderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock, LineElement, ElementProperties


class RenderingConfiguration(Generic[NODE_DATA]):
    def __init__(self,
                 header: Callable[[Node[NODE_DATA]], str],
                 header_style: Callable[[Node[NODE_DATA]], ElementProperties],
                 detail_indent: str,
                 ):
        self.header = header
        self.header_style = header_style
        self.detail_indent = detail_indent


class TreeRenderer(Generic[NODE_DATA], Renderer[MajorBlock]):
    def __init__(self,
                 configuration: RenderingConfiguration[NODE_DATA],
                 tree: Node[NODE_DATA],
                 ):
        self._tree = tree
        self._configuration = configuration

    def render(self) -> MajorBlock:
        return MajorBlock(_TreeRendererToMinorBlock(self._configuration, self._tree).render_sequence())


class _TreeRendererToMinorBlock(Generic[NODE_DATA], SequenceRenderer[MinorBlock]):
    def __init__(self,
                 configuration: RenderingConfiguration[NODE_DATA],
                 tree: Node[NODE_DATA],
                 ):
        self._tree = tree
        self._configuration = configuration

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
        node = self._tree
        s = self._configuration.header(node)

        return LineElement(
            structure.StringLineObject(s),
            self._configuration.header_style(self._tree),
        )

    def _children_renderer(self) -> SequenceRenderer[MinorBlock]:
        return rend_comb.ConcatenationR(
            [
                _TreeRendererToMinorBlock(self._configuration, child)
                for child in self._tree.children
            ]
        )

    def _details_renderer(self) -> SequenceRenderer[LineElement]:
        return rend_comb.ConcatenationR(
            [
                _DetailRendererToLineElements(self._configuration, detail)
                for detail in self._tree.details
            ]
        )


class _DetailRendererToLineElements(SequenceRenderer[LineElement],
                                    DetailVisitor[Sequence[LineElement]]):
    def __init__(self,
                 configuration: RenderingConfiguration,
                 detail: Detail,
                 ):
        self._detail = detail
        self._element_properties = ElementProperties(
            structure.Indentation(1, configuration.detail_indent)
        )

    def render_sequence(self) -> Sequence[LineElement]:
        return self._detail.accept(self)

    def visit_string(self, x: StringDetail) -> Sequence[LineElement]:
        return [
            LineElement(structure.StringLineObject(str(x.string)),
                        self._element_properties)
        ]

    def visit_pre_formatted_string(self, x: PreFormattedStringDetail) -> Sequence[LineElement]:
        return [
            LineElement(structure.PreFormattedStringLineObject(str(x.object_with_to_string),
                                                               x.string_is_line_ended),
                        self._element_properties)
        ]
