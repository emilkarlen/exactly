from typing import Sequence

from exactly_lib.symbol.resolver_structure import SymbolValueResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.value_type import TypeCategory, LogicValueType


class LogicValueResolver(SymbolValueResolver):
    """ Base class for logic values - values that represent functionality/logic."""

    @property
    def type_category(self) -> TypeCategory:
        return TypeCategory.LOGIC

    @property
    def logic_value_type(self) -> LogicValueType:
        raise NotImplementedError('abstract method')

    @property
    def references(self) -> Sequence[SymbolReference]:
        raise NotImplementedError('abstract method')


def get_logic_value_type(resolver: LogicValueResolver) -> LogicValueType:
    return resolver.logic_value_type
