from exactly_lib.symbol.logic.matcher import MatcherSdv, MatcherTypeStv
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel


class FileMatcherStv(MatcherTypeStv[FileMatcherModel]):
    def __init__(self, matcher: MatcherSdv[FileMatcherModel]):
        self._matcher = matcher

    @property
    def as_generic(self) -> MatcherSdv[FileMatcherModel]:
        return self._matcher

    def value(self) -> MatcherSdv[FileMatcherModel]:
        return self._matcher
