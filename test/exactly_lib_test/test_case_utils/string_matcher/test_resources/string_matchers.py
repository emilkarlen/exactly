from typing import Optional

from exactly_lib.type_system.error_message import ErrorMessageResolver
from exactly_lib.type_system.logic.string_matcher import StringMatcher, FileToCheck


class StringMatcherTestImplBase(StringMatcher):

    def matches(self, model: FileToCheck) -> Optional[ErrorMessageResolver]:
        self._matches_side_effects(model)
        return None

    def _matches_side_effects(self, model: FileToCheck):
        pass

    @property
    def option_description(self) -> str:
        return str(self)
