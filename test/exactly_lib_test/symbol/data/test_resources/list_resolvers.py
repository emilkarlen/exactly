from typing import Sequence

from exactly_lib.symbol.data.list_resolver import ListResolver, Element
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.data.list_ddv import ListDdv
from exactly_lib.util.symbol_table import SymbolTable


def arbitrary_resolver() -> ListResolver:
    return ListResolverTestImplForConstantListValue(ListDdv.empty())


class ListResolverTestImplForConstantListValue(ListResolver):
    def __init__(self, list_value: ListDdv):
        super().__init__([])
        self._list = list_value

    @property
    def elements(self) -> Sequence[Element]:
        return ()

    @property
    def references(self) -> Sequence[SymbolReference]:
        return ()

    def resolve(self, symbols: SymbolTable) -> ListDdv:
        return self._list
