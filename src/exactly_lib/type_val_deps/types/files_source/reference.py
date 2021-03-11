from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolContainer
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.sym_ref import restrictions
from exactly_lib.type_val_deps.types.files_source.ddv import FilesSourceDdv
from exactly_lib.type_val_deps.types.files_source.sdv import FilesSourceSdv
from exactly_lib.util.symbol_table import SymbolTable


class ReferenceSdv(FilesSourceSdv):
    def __init__(self, symbol_name: str):
        self._symbol_name = symbol_name
        self._references = (
            SymbolReference(symbol_name,
                            restrictions.ValueTypeRestriction.of_single(ValueType.FILES_SOURCE)),
        )

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> FilesSourceDdv:
        container = symbols.lookup(self._symbol_name)
        assert isinstance(container, SymbolContainer)
        sdv = container.sdv
        assert isinstance(sdv, FilesSourceSdv), 'Referenced symbol must be FilesSourceSdv'
        return sdv.resolve(symbols)
