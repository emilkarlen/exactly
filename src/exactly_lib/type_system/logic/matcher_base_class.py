from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.trace.trace_renderer import NodeRenderer
from exactly_lib.util.with_option_description import WithOptionDescription

T = TypeVar('T')


class Matcher(Generic[T], WithOptionDescription, ABC):
    """Matches a model."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    def matches(self, model: T) -> bool:
        return self.matches_emr(model) is None

    def matches_emr(self, model: T) -> ErrorMessageResolver:
        raise NotImplementedError('abstract method')


TraceRenderer = NodeRenderer[bool]


class MatchingResult:
    """The result of applying a matcher."""

    def __init__(self,
                 value: bool,
                 trace: TraceRenderer):
        self._value = value
        self._trace = trace

    @property
    def value(self) -> bool:
        return self._value

    @property
    def trace(self) -> TraceRenderer:
        return self._trace


class MatcherWTrace(Generic[T], Matcher[T], ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def matches_w_trace(self, model: T) -> MatchingResult:
        pass
