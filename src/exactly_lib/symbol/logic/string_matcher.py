from typing import List

from exactly_lib.symbol.logic.logic_type_sdv import LogicTypeSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.logic.string_matcher import StringMatcherDdv
from exactly_lib.type_system.value_type import LogicValueType, ValueType
from exactly_lib.util.symbol_table import SymbolTable


class StringMatcherSdv(LogicTypeSdv):
    """ Base class for SVDs of :class:`StringMatcherDdv`. """

    @property
    def logic_value_type(self) -> LogicValueType:
        return LogicValueType.STRING_MATCHER

    @property
    def value_type(self) -> ValueType:
        return ValueType.STRING_MATCHER

    @property
    def references(self) -> List[SymbolReference]:
        raise NotImplementedError('abstract method')

    def resolve(self, symbols: SymbolTable) -> StringMatcherDdv:
        raise NotImplementedError('abstract method')
