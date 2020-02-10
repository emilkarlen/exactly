from typing import Sequence

from exactly_lib.symbol.data.string_or_path import StringOrPathSdv
from exactly_lib.symbol.sdv_structure import SymbolReference, references_from_objects_with_symbol_references, \
    ObjectWithSymbolReferences
from exactly_lib.type_system.logic.program.stdin_data import StdinDataDdv
from exactly_lib.util.symbol_table import SymbolTable


class StdinDataSdv(ObjectWithSymbolReferences):
    def __init__(self, fragments: Sequence[StringOrPathSdv]):
        self._fragments = fragments

    def new_accumulated(self, stdin_data_sdv: 'StdinDataSdv') -> 'StdinDataSdv':
        assert isinstance(stdin_data_sdv, StdinDataSdv)

        fragments = tuple(self._fragments) + tuple(stdin_data_sdv._fragments)

        return StdinDataSdv(fragments)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return references_from_objects_with_symbol_references(self._fragments)

    def resolve_value(self, symbols: SymbolTable) -> StdinDataDdv:
        return StdinDataDdv([f.resolve(symbols) for f in self._fragments])


def no_stdin() -> StdinDataSdv:
    return StdinDataSdv(())
