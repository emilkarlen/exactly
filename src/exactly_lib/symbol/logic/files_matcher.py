from exactly_lib.symbol.logic.matcher import MatcherTypeStv, MatcherSdv
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel


class FilesMatcherStv(MatcherTypeStv[FilesMatcherModel]):
    def __init__(self, matcher: MatcherSdv[FilesMatcherModel]):
        self._matcher = matcher

    def value(self) -> MatcherSdv[FilesMatcherModel]:
        return self._matcher
