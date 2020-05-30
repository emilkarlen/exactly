from typing import Sequence

from exactly_lib.symbol import lookups
from exactly_lib.symbol.data.path_sdv import PathSdv, PathPartSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_system.data import paths
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib.util.symbol_table import SymbolTable


class PathSdvRelSymbol(PathSdv):
    def __init__(self,
                 path_suffix: PathPartSdv,
                 symbol_reference_of_path: SymbolReference):
        self.path_suffix = path_suffix
        self.symbol_reference_of_path = symbol_reference_of_path

    def resolve(self, symbols: SymbolTable) -> PathDdv:
        base_path = lookups.lookup_and_resolve_path(symbols, self.symbol_reference_of_path.name)
        suffix = self.path_suffix.resolve(symbols)
        return (
            paths.stacked(base_path, suffix)
            if suffix.value()
            else
            base_path
        )

    @property
    def references(self) -> Sequence[SymbolReference]:
        return [self.symbol_reference_of_path] + list(self.path_suffix.references)
