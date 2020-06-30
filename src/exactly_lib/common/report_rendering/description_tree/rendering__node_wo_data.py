from typing import Sequence

from exactly_lib.common.report_rendering.description_tree import layout__node_wo_data
from exactly_lib.util.description_tree import simple_textstruct_rendering as rendering
from exactly_lib.util.description_tree.tree import Node, Detail
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import Renderer, SequenceRenderer
from exactly_lib.util.simple_textstruct.rendering import component_renderers as comp_rend
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock


def as_major_block(tree: Node[None]) -> Renderer[MajorBlock]:
    return rendering.TreeRenderer(layout__node_wo_data.RENDERING_CONFIGURATION, tree)


def details_as_major_block(details: Sequence[Detail]) -> Renderer[MajorBlock]:
    return comp_rend.MajorBlockR(
        rend_comb.SingletonSequenceR(
            comp_rend.MinorBlockR(
                rendering.details_renderer_to_line_elements(layout__node_wo_data.RENDERING_CONFIGURATION, details)
            )
        )
    )


def as_minor_blocks(tree: Node[None]) -> SequenceRenderer[MinorBlock]:
    return rendering.TreeRendererToMinorBlocks(layout__node_wo_data.RENDERING_CONFIGURATION, tree)
