from exactly_lib.common.report_rendering.description_tree import layout__node_bool
from exactly_lib.util.description_tree import simple_textstruct_rendering
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.render.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock


class BoolTraceRenderer(Renderer[MajorBlock]):
    def __init__(self, trace: NodeRenderer[bool]):
        self._trace = trace

    def render(self) -> MajorBlock:
        return simple_textstruct_rendering.TreeRenderer(
            layout__node_bool.RENDERING_CONFIGURATION,
            self._trace.render()
        ).render()
