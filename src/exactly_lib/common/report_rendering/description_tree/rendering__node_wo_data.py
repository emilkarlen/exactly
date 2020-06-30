from typing import Sequence

from exactly_lib.common.report_rendering.description_tree import layout__node_wo_data
from exactly_lib.util.description_tree import simple_textstruct_rendering as rendering, simple_textstruct_rendering
from exactly_lib.util.description_tree.renderer import NodeRenderer, DetailsRenderer
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import Renderer, SequenceRenderer
from exactly_lib.util.simple_textstruct.rendering import component_renderers as comp_rend
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock


class NodeAsMajorBlockRenderer(Renderer[MajorBlock]):
    def __init__(self, node: NodeRenderer[None]):
        self._node = node

    def render(self) -> MajorBlock:
        return simple_textstruct_rendering.TreeRenderer(
            layout__node_wo_data.RENDERING_CONFIGURATION,
            self._node.render()
        ).render()


class NodeAsMinorBlocksRenderer(SequenceRenderer[MinorBlock]):
    def __init__(self, node: NodeRenderer[None]):
        self._node = node

    def render_sequence(self) -> Sequence[MinorBlock]:
        return rendering.TreeRendererToMinorBlocks(
            layout__node_wo_data.RENDERING_CONFIGURATION,
            self._node.render()
        ).render_sequence()


class DetailsAsMajorBlockRenderer(Renderer[MajorBlock]):
    def __init__(self, details: DetailsRenderer):
        self._details = details

    def render(self) -> MajorBlock:
        renderer = comp_rend.MajorBlockR(
            rend_comb.SingletonSequenceR(
                comp_rend.MinorBlockR(
                    rendering.details_renderer_to_line_elements(
                        layout__node_wo_data.RENDERING_CONFIGURATION,
                        self._details.render())
                )
            )
        )
        return renderer.render()
