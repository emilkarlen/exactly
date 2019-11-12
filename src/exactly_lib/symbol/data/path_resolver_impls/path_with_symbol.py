from typing import Sequence

from exactly_lib.symbol import lookups
from exactly_lib.symbol.data.path_resolver import PathResolver, PathPartResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.data import paths
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib.util.symbol_table import SymbolTable


class PathResolverRelSymbol(PathResolver):
    def __init__(self,
                 path_suffix: PathPartResolver,
                 symbol_reference_of_path: SymbolReference):
        self.path_suffix = path_suffix
        self.symbol_reference_of_path = symbol_reference_of_path

    def resolve(self, symbols: SymbolTable) -> PathDdv:
        base_path = lookups.lookup_and_resolve_path(symbols, self.symbol_reference_of_path.name)
        return paths.stacked(base_path, self.path_suffix.resolve(symbols))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return [self.symbol_reference_of_path] + list(self.path_suffix.references)
