from abc import ABC
from typing import Sequence

from exactly_lib.type_system.error_message import ErrorMessageResolvingEnvironment, ErrorMessageResolver
from exactly_lib.type_system.trace import trace
from exactly_lib.type_system.trace.trace import Detail, Node


class DetailRenderer(ABC):
    def render(self, environment: ErrorMessageResolvingEnvironment) -> Detail:
        pass


class NodeRenderer(ABC):
    def render(self, environment: ErrorMessageResolvingEnvironment) -> Node:
        pass


class NodeRendererFromParts(NodeRenderer):
    def __init__(self,
                 header: str,
                 details: Sequence[DetailRenderer],
                 children: Sequence[NodeRenderer]):
        self._header = header
        self._details = details
        self._children = children

    def render(self, environment: ErrorMessageResolvingEnvironment) -> Node:
        return Node(self._header,
                    [d.render(environment) for d in self._details],
                    [c.render(environment) for c in self._children],
                    )


class DetailRendererOfErrorMessageResolver(DetailRenderer):
    def __init__(self, message_resolver: ErrorMessageResolver):
        self._message_resolver = message_resolver

    def render(self, environment: ErrorMessageResolvingEnvironment) -> Detail:
        return trace.StringDetail(self._message_resolver.resolve(environment))


class DetailRendererOfConstant(DetailRenderer):
    def __init__(self, detail: Detail):
        self._detail = detail

    def render(self, environment: ErrorMessageResolvingEnvironment) -> Detail:
        return self._detail


class MatchingResult:
    """The result of applying a matcher."""

    def __init__(self,
                 value: bool,
                 trace: NodeRenderer):
        self._value = value
        self._trace = trace

    @property
    def value(self) -> bool:
        return self._value

    @property
    def trace(self) -> NodeRenderer:
        return self._trace
