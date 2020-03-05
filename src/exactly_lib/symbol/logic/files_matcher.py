from exactly_lib.symbol.logic.matcher import MatcherTypeStv, MatcherSdv
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel
from exactly_lib.type_system.value_type import LogicValueType, ValueType


class FilesMatcherStv(MatcherTypeStv[FilesMatcherModel]):
    def __init__(self, matcher: MatcherSdv[FilesMatcherModel]):
        self._matcher = matcher

    @property
    def logic_value_type(self) -> LogicValueType:
        return LogicValueType.FILES_MATCHER

    @property
    def value_type(self) -> ValueType:
        return ValueType.FILES_MATCHER

    def value(self) -> MatcherSdv[FilesMatcherModel]:
        return self._matcher
