from typing import List

from exactly_lib.type_system.trace.trace_rendering import NodeRenderer, DetailRenderer, NodeRendererFromParts, \
    MatchingResult


class TraceBuilder:
    def __init__(self, header: str):
        self._header = header
        self._details = []
        self._children = []
        self._result_value = None

    def with_result_value(self, result_value: bool) -> 'TraceBuilder':
        self._result_value = result_value
        return self

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
                              self.with_result_value(value).build()
                              )

    def build(self) -> NodeRenderer:
        # TODO Generate DetailRenderer from _result, if not None.
        # if self._result is not None:
        #   self._details.insert(0,ConstDetailRenderer(ResultDetail(self._result))
        return NodeRendererFromParts(
            self._header,
            self._details,
            self._children,
        )
