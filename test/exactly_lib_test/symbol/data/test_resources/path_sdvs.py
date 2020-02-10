from typing import Sequence

from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.type_system.data import paths
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib.util.symbol_table import SymbolTable


def arbitrary_sdv() -> PathSdv:
    return PathSdvTestImplWithConstantPathAndSymbolReferences(
        paths.simple_of_rel_option(RelOptionType.REL_ACT, 'base-name'),
        (),
    )


class PathSdvTestImplWithConstantPathAndSymbolReferences(PathSdv):
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
