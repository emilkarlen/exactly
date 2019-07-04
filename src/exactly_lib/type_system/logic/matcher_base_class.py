from abc import ABC
from typing import TypeVar, Generic

from exactly_lib.type_system.trace.trace_rendering import MatchingResult
from exactly_lib.util.with_option_description import WithOptionDescription

T = TypeVar('T')


class Matcher(Generic[T], WithOptionDescription, ABC):
    """Matches a model."""

    def matches(self, model: T) -> bool:
        raise NotImplementedError('abstract method')


class MatcherWTrace(Generic[T], Matcher[T], ABC):
    @property
    def name(self) -> str:
        pass

    def matches_w_trace(self, model: T) -> MatchingResult:
        pass
