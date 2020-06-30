from exactly_lib.util import ansi_terminal_color
from exactly_lib.util.description_tree import simple_textstruct_rendering as rendering
from exactly_lib.util.description_tree.tree import Node
from exactly_lib.util.simple_textstruct import structure

STRUCTURE_NODE_HEADER_TEXT_STYLE = structure.TextStyle(
    color=ansi_terminal_color.ForegroundColor.CYAN
)

RENDERING_CONFIGURATION = rendering.RenderingConfiguration(
    Node.header.fget,
    lambda node_data: rendering.ElementProperties(
        text_style=STRUCTURE_NODE_HEADER_TEXT_STYLE
    ),
    structure.INDENTATION__1,
    '',
)
