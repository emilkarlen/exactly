from typing import Optional

from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, MatcherWTrace
from exactly_lib.type_system.logic.string_matcher import StringMatcher, FileToCheck


class StringMatcherDelegatedToMatcherWTrace(StringMatcher):
    def __init__(self, delegated: MatcherWTrace[FileToCheck]):
        self._delegated = delegated

    @property
    def name(self) -> str:
        return self._delegated.name

    @property
    def option_description(self) -> str:
        return self._delegated.option_description

    def matches(self, model: FileToCheck) -> bool:
        return self._delegated.matches(model)

    def matches_emr(self, model: FileToCheck) -> Optional[ErrorMessageResolver]:
        return self._delegated.matches_emr(model)

    def matches_w_trace(self, model: FileToCheck) -> MatchingResult:
        return self._delegated.matches_w_trace(model)
