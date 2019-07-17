from abc import ABC
from typing import Sequence, TypeVar, Generic

from exactly_lib.type_system.error_message import ErrorMessageResolvingEnvironment, ErrorMessageResolver
from exactly_lib.type_system.trace import trace
from exactly_lib.type_system.trace.trace import Detail, Node


class DetailRenderer(ABC):
    def render(self, environment: ErrorMessageResolvingEnvironment) -> Detail:
        pass


NODE_DATA = TypeVar('NODE_DATA')


class NodeRenderer(Generic[NODE_DATA], ABC):
    def render(self, environment: ErrorMessageResolvingEnvironment) -> Node[NODE_DATA]:
        pass


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

    def render(self, environment: ErrorMessageResolvingEnvironment) -> Node[NODE_DATA]:
        return Node(self._header,
                    self._data,
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
