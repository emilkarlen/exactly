from typing import List

from exactly_lib.type_system.trace.trace_rendering import NodeRenderer, DetailRenderer, NodeRendererFromParts, \
    MatchingResult


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
    def children(self) -> List[NodeRenderer]:
        return self._children

    def append_child(self, child: NodeRenderer) -> 'TraceBuilder':
        self._children.append(child)
        return self

    def build_result(self, value: bool) -> MatchingResult:
        return MatchingResult(value,
                              self.build_bool(value)
                              )

    def build_bool(self, data: bool) -> NodeRenderer[bool]:
        return NodeRendererFromParts(
            self._header,
            data,
            self._details,
            self._children,
        )

    def build_none(self) -> NodeRenderer[None]:
        return NodeRendererFromParts(
            self._header,
            None,
            self._details,
            self._children,
        )
