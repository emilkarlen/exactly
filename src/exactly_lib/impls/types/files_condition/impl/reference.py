from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.sym_ref import restrictions, symbol_lookup
from exactly_lib.type_val_deps.types.files_condition.sdv import FilesConditionSdv, FilesConditionDdv
from exactly_lib.util.symbol_table import SymbolTable


class ReferenceSdv(FilesConditionSdv):
    def __init__(self, symbol_name: str):
        self._symbol_name = symbol_name
        self._references = (
            SymbolReference(symbol_name,
                            restrictions.ValueTypeRestriction.of_single(ValueType.FILES_CONDITION)),
        )

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> FilesConditionDdv:
        referenced_sdv = symbol_lookup.lookup_files_condition(symbols, self._symbol_name)
        return referenced_sdv.resolve(symbols)
