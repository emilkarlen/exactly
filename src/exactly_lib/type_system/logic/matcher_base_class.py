from abc import ABC
from typing import TypeVar, Generic

from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.trace.trace_rendering import NodeRenderer
from exactly_lib.util.with_option_description import WithOptionDescription

T = TypeVar('T')


class Matcher(Generic[T], WithOptionDescription, ABC):
    """Matches a model."""

    def matches(self, model: T) -> bool:
        raise NotImplementedError('abstract method')

    def matches_emr(self, model: T) -> ErrorMessageResolver:
        raise NotImplementedError('abstract method')


class MatchingResult:
    """The result of applying a matcher."""

    def __init__(self,
                 value: bool,
                 trace: NodeRenderer[bool]):
        self._value = value
        self._trace = trace

    @property
    def value(self) -> bool:
        return self._value

    @property
    def trace(self) -> NodeRenderer[bool]:
        return self._trace


class MatcherWTrace(Generic[T], Matcher[T], ABC):
    @property
    def name(self) -> str:
        pass

    def matches_w_trace(self, model: T) -> MatchingResult:
        pass
