from typing import Sequence

from exactly_lib.symbol.data.path_resolver import PathResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib.util.symbol_table import SymbolTable


class PathConstant(PathResolver):
    """
    A `PathResolver` that is a constant `PathDdv`
    """

    def __init__(self, path: PathDdv):
        self._path = path

    def resolve(self, symbols: SymbolTable) -> PathDdv:
        return self._path

    @property
    def references(self) -> Sequence[SymbolReference]:
        return ()

    def __str__(self):
        return str(type(self)) + '\'' + str(self._path) + '\''
