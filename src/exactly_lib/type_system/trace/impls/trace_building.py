from typing import List

from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.type_system.trace.impls.trace_renderers import NodeRendererFromParts
from exactly_lib.type_system.trace.trace import Node
from exactly_lib.type_system.trace.trace_renderer import NodeRenderer, DetailRenderer, NODE_DATA


class TraceBuilder:
    def __init__(self, header: str):
        self._header = header
        self._details = []
        self._children = []

    @property
    def details(self) -> List[DetailRenderer]:
        return self._details

    def append_detail(self, detail: DetailRenderer) -> 'TraceBuilder':
        self._details.append(detail)
        return self

    @property
    def children(self) -> List[NodeRenderer[bool]]:
        return self._children

    def append_child(self, child: NodeRenderer[bool]) -> 'TraceBuilder':
        self._children.append(child)
        return self

    def build_result(self, value: bool) -> MatchingResult:
        return MatchingResult(value,
                              self.as_render(value)
                              )

    def build_bool(self, data: bool) -> NodeRenderer[bool]:
        return NodeRendererFromParts(
            self._header,
            data,
            self._details,
            self._children,
        )

    def as_render(self, data: bool) -> NodeRenderer[bool]:
        return _NodeRendererFromBuilder(data, self)


class _NodeRendererFromBuilder(NodeRenderer[bool]):
    def __init__(self,
                 data: bool,
                 builder: TraceBuilder,
                 ):
        self._data = data
        self._builder = builder

    def render(self) -> Node[NODE_DATA]:
        return self._builder.build_bool(self._data).render()