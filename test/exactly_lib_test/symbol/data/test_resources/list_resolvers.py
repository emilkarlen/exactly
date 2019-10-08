from typing import Sequence

from exactly_lib.symbol.data.list_resolver import ListResolver, Element
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.data.list_value import ListValue
from exactly_lib.util.symbol_table import SymbolTable


def arbitrary_resolver() -> ListResolver:
    return ListResolverTestImplForConstantListValue(ListValue.empty())


class ListResolverTestImplForConstantListValue(ListResolver):
    def __init__(self, list_value: ListValue):
        super().__init__([])
        self._list_value = list_value

    @property
    def elements(self) -> Sequence[Element]:
        return ()

    @property
    def references(self) -> Sequence[SymbolReference]:
        return ()

    def resolve(self, symbols: SymbolTable) -> ListValue:
        return self._list_value
