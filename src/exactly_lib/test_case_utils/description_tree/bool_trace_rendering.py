from exactly_lib.util.ansi_terminal_color import ForegroundColor
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.description_tree.simple_textstruct_rendering import TreeRenderer, RenderingConfiguration
from exactly_lib.util.description_tree.tree import Node
from exactly_lib.util.render.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock, ElementProperties, INDENTATION__NEUTRAL, TextStyle, \
    Indentation


class BoolTraceRenderer(Renderer[MajorBlock]):
    def __init__(self, trace: NodeRenderer[bool]):
        self._trace = trace

    def render(self) -> MajorBlock:
        return TreeRenderer(_RENDERING_CONFIGURATION, self._trace.render()).render()


def _make_header(node: Node[bool]) -> str:
    bool_char = bool_string(node.data)

    return '({}) {}'.format(bool_char, node.header)


def bool_string(b: bool) -> str:
    return 'T' if b else 'F'


# Makes details at level 0 appear aligned with the node header
DETAILS_INDENT = ' ' * len('(B) ')
MINOR_BLOCKS_INDENT_INCREASE = Indentation(1, '  ')

_HEADER_PROPERTIES_FOR_F = ElementProperties(INDENTATION__NEUTRAL, TextStyle(color=ForegroundColor.BRIGHT_RED))
_HEADER_PROPERTIES_FOR_T = ElementProperties(INDENTATION__NEUTRAL, TextStyle(color=ForegroundColor.BRIGHT_GREEN))


def _get_header_style(node: Node[bool]) -> ElementProperties:
    return (
        _HEADER_PROPERTIES_FOR_T
        if node.data
        else
        _HEADER_PROPERTIES_FOR_F
    )


_RENDERING_CONFIGURATION = RenderingConfiguration(
    _make_header,
    _get_header_style,
    MINOR_BLOCKS_INDENT_INCREASE,
    DETAILS_INDENT,
)
