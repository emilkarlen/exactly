from typing import Sequence

from exactly_lib.impls.types.string_source import sdvs
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolContainer
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.sym_ref import restrictions
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib.type_val_deps.types.string_source.ddv import StringSourceDdv
from exactly_lib.type_val_deps.types.string_source.sdv import StringSourceSdv
from exactly_lib.util.symbol_table import SymbolTable


class SymbolReferenceStringStringSourceSdv(StringSourceSdv):
    ACCEPTED_REFERENCED_TYPES = (ValueType.STRING_SOURCE, ValueType.STRING)
    REFERENCE_RESTRICTIONS = restrictions.ValueTypeRestriction(
        ACCEPTED_REFERENCED_TYPES
    )

    def __init__(self, symbol_name: str):
        self._symbol_name = symbol_name
        self._references = (SymbolReference(symbol_name,
                                            self.REFERENCE_RESTRICTIONS),)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> StringSourceDdv:
        container = symbols.lookup(self._symbol_name)
        assert isinstance(container, SymbolContainer)  # Type info for IDE
        sdv = container.sdv
        if isinstance(sdv, StringSourceSdv):
            return sdv.resolve(symbols)
        elif isinstance(sdv, StringSdv):
            return sdvs.ConstantStringStringSourceSdv(sdv).resolve(symbols)
        else:
            raise TypeError('Expected string-source or string, found: ' + str(container.value_type))
