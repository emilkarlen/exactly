from typing import List

from exactly_lib.symbol.logic.logic_type_sdv import MatcherTypeSdv
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.logic.file_matcher import FileMatcherDdv, FileMatcherModel
from exactly_lib.type_system.value_type import LogicValueType, ValueType
from exactly_lib.util.symbol_table import SymbolTable


class FileMatcherSdv(MatcherTypeSdv[FileMatcherModel]):
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

    @property
    def references(self) -> List[SymbolReference]:
        return list(self._matcher.references)

    def resolve(self, symbols: SymbolTable) -> FileMatcherDdv:
        return self._matcher.resolve(symbols)
