from exactly_lib.symbol.logic.matcher import MatcherSdv, MatcherTypeStv
from exactly_lib.type_system.logic.string_matcher import FileToCheck


class StringMatcherStv(MatcherTypeStv[FileToCheck]):
    def __init__(self, matcher: MatcherSdv[FileToCheck]):
        self._matcher = matcher

    @property
    def as_generic(self) -> MatcherSdv[FileToCheck]:
        return self._matcher

    def value(self) -> MatcherSdv[FileToCheck]:
        return self._matcher
