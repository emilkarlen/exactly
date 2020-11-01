from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_deps.sym_ref import symbol_lookup
from exactly_lib.type_val_deps.types.path import path_ddvs
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv, PathPartSdv
from exactly_lib.util.symbol_table import SymbolTable


class PathSdvRelSymbol(PathSdv):
    def __init__(self,
                 path_suffix: PathPartSdv,
                 relativity: SymbolReference):
        self.path_suffix = path_suffix
        self.relativity = relativity

    def resolve(self, symbols: SymbolTable) -> PathDdv:
        base_path = symbol_lookup.lookup_and_resolve_path(symbols, self.relativity.name)
        suffix = self.path_suffix.resolve(symbols)
        return (
            path_ddvs.stacked(base_path, suffix)
            if suffix.value()
            else
            base_path
        )

    @property
    def references(self) -> Sequence[SymbolReference]:
        return [self.relativity] + list(self.path_suffix.references)
