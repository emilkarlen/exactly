from exactly_lib.util import ansi_terminal_color
from exactly_lib.util.description_tree import simple_textstruct_rendering as rendering
from exactly_lib.util.description_tree.tree import Node
from exactly_lib.util.render.renderer import Renderer, SequenceRenderer
from exactly_lib.util.simple_textstruct import structure as text_struct
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock

TREE_LAYOUT = rendering.RenderingConfiguration(
    Node.header.fget,
    lambda node_data: rendering.ElementProperties(
        text_style=text_struct.TextStyle(color=ansi_terminal_color.ForegroundColor.CYAN)
    ),
    '',
)


def as_major_block(tree: Node[None]) -> Renderer[MajorBlock]:
    return rendering.TreeRenderer(TREE_LAYOUT, tree)


def as_minor_blocks(tree: Node[None]) -> SequenceRenderer[MinorBlock]:
    return rendering.TreeRendererToMinorBlocks(TREE_LAYOUT, tree)
