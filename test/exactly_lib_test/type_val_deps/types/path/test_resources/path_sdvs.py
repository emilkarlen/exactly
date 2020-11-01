from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_deps.types.path import path_ddvs
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.util.symbol_table import SymbolTable


def arbitrary_sdv() -> PathSdv:
    return PathSdvTestImplWithConstantPathAndSymbolReferences(
        path_ddvs.simple_of_rel_option(RelOptionType.REL_ACT, 'base-name'),
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
