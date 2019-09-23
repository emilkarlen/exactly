from typing import Generic, Sequence

from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.trace import trace
from exactly_lib.type_system.trace.trace import Node, Detail
from exactly_lib.type_system.trace.trace_renderer import NODE_DATA, NodeRenderer, DetailRenderer


class NodeRendererFromParts(Generic[NODE_DATA], NodeRenderer[NODE_DATA]):
    def __init__(self,
                 header: str,
                 data: NODE_DATA,
                 details: Sequence[DetailRenderer],
                 children: Sequence[NodeRenderer[NODE_DATA]]):
        self._header = header
        self._data = data
        self._details = details
        self._children = children

    def render(self) -> Node[NODE_DATA]:
        return Node(self._header,
                    self._data,
                    [d.render() for d in self._details],
                    [c.render() for c in self._children],
                    )


class DetailRendererOfErrorMessageResolver(DetailRenderer):
    def __init__(self, message_resolver: ErrorMessageResolver):
        self._message_resolver = message_resolver

    def render(self) -> Detail:
        return trace.StringDetail(self._message_resolver.resolve())


class DetailRendererOfConstant(DetailRenderer):
    def __init__(self, detail: Detail):
        self._detail = detail

    def render(self) -> Detail:
        return self._detail
