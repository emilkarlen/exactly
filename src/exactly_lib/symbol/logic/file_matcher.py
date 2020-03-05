from exactly_lib.symbol.logic.matcher import MatcherSdv, MatcherTypeStv
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.value_type import LogicValueType, ValueType


class FileMatcherStv(MatcherTypeStv[FileMatcherModel]):
    def __init__(self, matcher: MatcherSdv[FileMatcherModel]):
        self._matcher = matcher

    @property
    def logic_value_type(self) -> LogicValueType:
        return LogicValueType.FILE_MATCHER

    @property
    def value_type(self) -> ValueType:
        return ValueType.FILE_MATCHER

    @property
    def as_generic(self) -> MatcherSdv[FileMatcherModel]:
        return self._matcher

    def value(self) -> MatcherSdv[FileMatcherModel]:
        return self._matcher
