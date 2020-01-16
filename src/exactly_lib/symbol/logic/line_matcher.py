from typing import List

from exactly_lib.symbol.logic.logic_type_sdv import MatcherTypeSdv
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.logic.line_matcher import LineMatcherDdv, LineMatcherLine
from exactly_lib.type_system.value_type import LogicValueType, ValueType
from exactly_lib.util.symbol_table import SymbolTable


class LineMatcherSdv(MatcherTypeSdv[LineMatcherLine]):
    """ Base class for SDVs of :class:`LineMatcher`. """

    def __init__(self, matcher: MatcherSdv[LineMatcherLine]):
        self._matcher = matcher

    @property
    def logic_value_type(self) -> LogicValueType:
        return LogicValueType.LINE_MATCHER

    @property
    def value_type(self) -> ValueType:
        return ValueType.LINE_MATCHER

    @property
    def as_generic(self) -> MatcherSdv[LineMatcherLine]:
        return self._matcher

    @property
    def references(self) -> List[SymbolReference]:
        return list(self._matcher.references)

    def resolve(self, symbols: SymbolTable) -> LineMatcherDdv:
        return self._matcher.resolve(symbols)
