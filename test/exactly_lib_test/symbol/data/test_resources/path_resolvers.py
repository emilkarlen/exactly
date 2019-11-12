from typing import Sequence

from exactly_lib.symbol.data.path_resolver import PathResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.type_system.data import paths
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib.util.symbol_table import SymbolTable


def arbitrary_resolver() -> PathResolver:
    return PathResolverTestImplWithConstantPathAndSymbolReferences(
        paths.simple_of_rel_option(RelOptionType.REL_ACT, 'base-name'),
        (),
    )


class PathResolverTestImplWithConstantPathAndSymbolReferences(PathResolver):
    def __init__(self,
                 path: PathDdv,
                 references: Sequence[SymbolReference]):
        self._path = path
        self._references = references

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> PathDdv:
        return self._path
