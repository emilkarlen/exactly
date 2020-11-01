from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_deps.types.list_.list_ddv import ListDdv
from exactly_lib.type_val_deps.types.list_.list_sdv import ListSdv, ElementSdv
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
