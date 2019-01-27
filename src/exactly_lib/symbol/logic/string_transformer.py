from typing import List

from exactly_lib.symbol.logic.logic_value_resolver import LogicValueResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.logic.string_transformer import StringTransformerValue
from exactly_lib.type_system.value_type import LogicValueType, ValueType
from exactly_lib.util.symbol_table import SymbolTable


class StringTransformerResolver(LogicValueResolver):
    @property
    def logic_value_type(self) -> LogicValueType:
        return LogicValueType.STRING_TRANSFORMER

    @property
    def value_type(self) -> ValueType:
        return ValueType.STRING_TRANSFORMER

    @property
    def references(self) -> List[SymbolReference]:
        raise NotImplementedError('abstract method')

    def resolve(self, symbols: SymbolTable) -> StringTransformerValue:
        raise NotImplementedError('abstract method')
