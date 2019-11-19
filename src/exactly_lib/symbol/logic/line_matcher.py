from typing import List

from exactly_lib.symbol.logic.logic_type_sdv import LogicTypeSdv
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.logic.line_matcher import LineMatcherDdv, LineMatcherLine
from exactly_lib.type_system.value_type import LogicValueType, ValueType
from exactly_lib.util.symbol_table import SymbolTable


class LineMatcherSdv(LogicTypeSdv, MatcherSdv[LineMatcherLine]):
    """ Base class for SDVs of :class:`LineMatcher`. """

    @property
    def logic_value_type(self) -> LogicValueType:
        return LogicValueType.LINE_MATCHER

    @property
    def value_type(self) -> ValueType:
        return ValueType.LINE_MATCHER

    @property
    def references(self) -> List[SymbolReference]:
        raise NotImplementedError('abstract method')

    def resolve(self, symbols: SymbolTable) -> LineMatcherDdv:
        raise NotImplementedError('abstract method')
