from typing import List

from exactly_lib.symbol.logic.logic_type_sdv import MatcherTypeSdv
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv
from exactly_lib.type_system.logic.string_matcher import FileToCheck
from exactly_lib.type_system.value_type import LogicValueType, ValueType
from exactly_lib.util.symbol_table import SymbolTable


class StringMatcherSdv(MatcherTypeSdv[FileToCheck]):
    def __init__(self, matcher: MatcherSdv[FileToCheck]):
        self._matcher = matcher

    @property
    def logic_value_type(self) -> LogicValueType:
        return LogicValueType.STRING_MATCHER

    @property
    def value_type(self) -> ValueType:
        return ValueType.STRING_MATCHER

    @property
    def as_generic(self) -> MatcherSdv[FileToCheck]:
        return self._matcher

    @property
    def references(self) -> List[SymbolReference]:
        return list(self._matcher.references)

    def resolve(self, symbols: SymbolTable) -> MatcherDdv[FileToCheck]:
        return self._matcher.resolve(symbols)
