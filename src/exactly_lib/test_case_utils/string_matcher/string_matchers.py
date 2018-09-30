from typing import Optional

from exactly_lib.type_system.error_message import ErrorMessageResolver
from exactly_lib.type_system.logic.string_matcher import StringMatcher, FileToCheck


class StringMatcherConstant(StringMatcher):
    """Matcher with constant result."""

    def __init__(self, result: Optional[ErrorMessageResolver]):
        self._result = result

    @property
    def option_description(self) -> str:
        return 'any string' if self._result else 'no string'

    @property
    def result_constant(self) -> Optional[ErrorMessageResolver]:
        return self._result

    def matches(self, model: FileToCheck) -> Optional[ErrorMessageResolver]:
        return self._result
