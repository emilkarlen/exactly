from typing import Sequence, Generic, Callable

from exactly_lib.util.description_tree.tree import Node, Detail, DetailVisitor, StringDetail, PreFormattedStringDetail, \
    NODE_DATA, HeaderAndValueDetail, TreeDetail, IndentedDetail
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import SequenceRenderer, Renderer
from exactly_lib.util.simple_textstruct import structure
from exactly_lib.util.simple_textstruct.rendering import elements
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
        return MajorBlock(TreeRendererToMinorBlocks(self._configuration, self._tree).render_sequence())


class TreeRendererToMinorBlocks(Generic[NODE_DATA], SequenceRenderer[MinorBlock]):
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
                TreeRendererToMinorBlocks(self._configuration, child)
                for child in self._tree.children
            ]
        )

    def _details_renderer(self) -> SequenceRenderer[LineElement]:
        return rend_comb.ConcatenationR(
            [
                _LineElementRendererForDetail(self._configuration, 0, detail)
                for detail in self._tree.details
            ]
        )


class _LineElementRendererForDetail(SequenceRenderer[LineElement],
                                    DetailVisitor[Sequence[LineElement]]):
    def __init__(self,
                 configuration: RenderingConfiguration,
                 depth: int,
                 detail: Detail,
                 ):
        self._configuration = configuration
        self._depth = depth
        self._detail = detail
        self._indent_suffix = configuration.detail_indent
        self._root_element_properties = ElementProperties(
            structure.Indentation(depth + 1, self._indent_suffix)
        )

    def render_sequence(self) -> Sequence[LineElement]:
        return self._detail.accept(self)

    def visit_string(self, x: StringDetail) -> Sequence[LineElement]:
        return [
            LineElement(structure.StringLineObject(str(x.string)),
                        self._root_element_properties)
        ]

    def visit_pre_formatted_string(self, x: PreFormattedStringDetail) -> Sequence[LineElement]:
        return [
            LineElement(structure.PreFormattedStringLineObject(str(x.object_with_to_string),
                                                               x.string_is_line_ended),
                        self._root_element_properties)
        ]

    def visit_header_and_value(self, x: HeaderAndValueDetail) -> Sequence[LineElement]:
        value_elements_renderer = rend_comb.ConcatenationR([
            self._renderer_for_next_depth(value)
            for value in x.values
        ])

        ret_val = [
            LineElement(structure.StringLineObject(str(x.header)),
                        self._root_element_properties)
        ]

        ret_val += value_elements_renderer.render_sequence()

        return ret_val

    def visit_indented(self, x: IndentedDetail) -> Sequence[LineElement]:
        details_renderer = rend_comb.ConcatenationR([
            self._renderer_for_next_depth(value)
            for value in x.details
        ])

        return details_renderer.render_sequence()

    def visit_tree(self, x: TreeDetail) -> Sequence[LineElement]:
        tree = x.tree

        details_renderer = rend_comb.ConcatenationR([
            self._renderer_for_next_depth(detail)
            for detail in tree.details
        ])

        children_renderer = rend_comb.ConcatenationR([
            self._renderer_for_next_depth(TreeDetail(child))
            for child in tree.children
        ])

        ret_val = [
            LineElement(structure.StringLineObject(str(tree.header)),
                        self._root_element_properties)
        ]
        ret_val += details_renderer.render_sequence()
        ret_val += children_renderer.render_sequence()

        return ret_val

    def _renderer_for_next_depth(self, detail: Detail) -> SequenceRenderer[LineElement]:
        return _LineElementRendererForDetail(self._configuration, self._depth + 1, detail)
