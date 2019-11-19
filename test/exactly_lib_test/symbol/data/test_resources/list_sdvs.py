from typing import Sequence

from exactly_lib.symbol.data.list_sdv import ListSdv, ElementSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.data.list_ddv import ListDdv
from exactly_lib.util.symbol_table import SymbolTable


def arbitrary_sdv() -> ListSdv:
    return ListSdvTestImplForConstantListDdv(ListDdv.empty())


class ListSdvTestImplForConstantListDdv(ListSdv):
    def __init__(self, ddv: ListDdv):
        super().__init__([])
        self._ddv = ddv

    @property
    def elements(self) -> Sequence[ElementSdv]:
        return ()

    @property
    def references(self) -> Sequence[SymbolReference]:
        return ()

    def resolve(self, symbols: SymbolTable) -> ListDdv:
        return self._ddv
