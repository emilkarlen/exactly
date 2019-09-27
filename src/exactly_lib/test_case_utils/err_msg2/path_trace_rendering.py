from exactly_lib.type_system.data.described_path import DescribedPathPrimitive
from exactly_lib.type_system.trace import trace
from exactly_lib.type_system.trace.trace import Detail
from exactly_lib.type_system.trace.trace_renderer import DetailRenderer


class PathDetailRenderer(DetailRenderer):
    def __init__(self, path: DescribedPathPrimitive):
        self._path = path

    def render(self) -> Detail:
        return trace.StringDetail(self._path.describer.value.render())
