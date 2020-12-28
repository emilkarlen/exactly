from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolReference, ReferenceRestrictions
from exactly_lib.type_val_deps.sym_ref.data.reference_restrictions import is_any_data_type
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.type_val_deps.types.string_.string_ddv import StringDdv
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv, StringFragmentSdv
from exactly_lib.type_val_deps.types.string_.strings_ddvs import ConstantFragmentDdv
from exactly_lib.util.symbol_table import SymbolTable


def arbitrary_sdv() -> StringSdv:
    return StringSdvTestImpl('arbitrary value')


def string_sdv_of_single_symbol_reference(
        symbol_name: str,
        restrictions: ReferenceRestrictions = is_any_data_type()) -> StringSdv:
    symbol_reference = SymbolReference(symbol_name,
                                       restrictions)
    fragments = [
        string_sdvs.symbol_fragment(symbol_reference)
    ]
    return StringSdv(tuple(fragments))


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
