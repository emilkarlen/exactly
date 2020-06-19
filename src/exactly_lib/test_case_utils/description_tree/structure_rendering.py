from typing import Sequence

from exactly_lib.util import ansi_terminal_color
from exactly_lib.util.description_tree import simple_textstruct_rendering as rendering
from exactly_lib.util.description_tree.tree import Node, Detail
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import Renderer, SequenceRenderer
from exactly_lib.util.simple_textstruct import structure as text_struct, structure
from exactly_lib.util.simple_textstruct.rendering import component_renderers as comp_rend
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock

STRUCTURE_NODE_TEXT_COLOR = ansi_terminal_color.ForegroundColor.CYAN

TREE_LAYOUT = rendering.RenderingConfiguration(
    Node.header.fget,
    lambda node_data: rendering.ElementProperties(
        text_style=text_struct.TextStyle(color=STRUCTURE_NODE_TEXT_COLOR)
    ),
    structure.INDENTATION__1,
    '',
)


def as_major_block(tree: Node[None]) -> Renderer[MajorBlock]:
    return rendering.TreeRenderer(TREE_LAYOUT, tree)


def details_as_major_block(details: Sequence[Detail]) -> Renderer[MajorBlock]:
    return comp_rend.MajorBlockR(
        rend_comb.SingletonSequenceR(
            comp_rend.MinorBlockR(
                rendering.details_renderer_to_line_elements(TREE_LAYOUT, details)
            )
        )
    )


def as_minor_blocks(tree: Node[None]) -> SequenceRenderer[MinorBlock]:
    return rendering.TreeRendererToMinorBlocks(TREE_LAYOUT, tree)
