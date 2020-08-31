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
                 relativity: SymbolReference):
        self.path_suffix = path_suffix
        self.relativity = relativity

    def resolve(self, symbols: SymbolTable) -> PathDdv:
        base_path = lookups.lookup_and_resolve_path(symbols, self.relativity.name)
        suffix = self.path_suffix.resolve(symbols)
        return (
            paths.stacked(base_path, suffix)
            if suffix.value()
            else
            base_path
        )

    @property
    def references(self) -> Sequence[SymbolReference]:
        return [self.relativity] + list(self.path_suffix.references)
