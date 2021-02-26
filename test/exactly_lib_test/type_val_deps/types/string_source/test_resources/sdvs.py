from abc import ABC
from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_deps.types.string_source.ddv import StringSourceDdv
from exactly_lib.type_val_deps.types.string_source.sdv import StringSourceSdv
from exactly_lib.util.symbol_table import SymbolTable


class StringSourceSdvTestImplBase(StringSourceSdv, ABC):
    pass


class StringSourceSdvConstantTestImpl(StringSourceSdvTestImplBase):
    def __init__(self, ddv: StringSourceDdv):
        self._ddv = ddv

    @property
    def references(self) -> Sequence[SymbolReference]:
        return ()

    def resolve(self, symbols: SymbolTable) -> StringSourceDdv:
        return self._ddv
