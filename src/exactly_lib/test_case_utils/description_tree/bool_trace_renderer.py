from exactly_lib.type_system.trace.trace_renderer import NodeRenderer
from exactly_lib.util.description_tree.rendering import TreeRenderer
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock


class BoolTraceRenderer(Renderer[MajorBlock]):
    def __init__(self, trace: NodeRenderer[bool]):
        self._trace = trace

    def render(self) -> MajorBlock:
        return TreeRenderer(self._trace.render()).render()
