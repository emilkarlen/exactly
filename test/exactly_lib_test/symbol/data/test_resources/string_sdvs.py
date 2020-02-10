from typing import Sequence

from exactly_lib.symbol.data.string_sdv import StringSdv, StringFragmentSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_system.data.concrete_strings import ConstantFragmentDdv
from exactly_lib.type_system.data.string_ddv import StringDdv
from exactly_lib.util.symbol_table import SymbolTable


def arbitrary_sdv() -> StringSdv:
    return StringSdvTestImpl('arbitrary value')


class StringSdvTestImpl(StringSdv):
    def __init__(self,
                 value: str,
                 explicit_references: Sequence[SymbolReference] = (),
                 fragment_sdvs: Sequence[StringFragmentSdv] = ()):
        super().__init__(fragment_sdvs)
        self.value = value
        self.explicit_references = explicit_references
        self._fragments = fragment_sdvs

    def resolve(self, symbols: SymbolTable) -> StringDdv:
        return StringDdv((ConstantFragmentDdv(self.value),))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self.explicit_references
