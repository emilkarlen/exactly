from typing import TypeVar, Generic

from exactly_lib.util.with_option_description import WithOptionDescription

T = TypeVar('T')


class Matcher(Generic[T], WithOptionDescription):
    """Matches a model."""

    def matches(self, model) -> bool:
        raise NotImplementedError('abstract method')
