from typing import Sequence

from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.data.list_value import ListValue
from exactly_lib.util.symbol_table import SymbolTable


class ListResolverTestImplForConstantListValue(ListResolver):
    def __init__(self, list_value: ListValue):
        super().__init__([])
        self._list_value = list_value

    @property
    def elements(self) -> tuple:
        raise ValueError('this method is not supported')

    @property
    def references(self) -> Sequence[SymbolReference]:
        return ()

    def resolve(self, symbols: SymbolTable) -> ListValue:
        return self._list_value
