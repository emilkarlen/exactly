from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.type_val_deps.types.string.string_sdv import StringSdv
from exactly_lib.type_val_deps.types.string_model.ddv import StringModelDdv
from exactly_lib.type_val_deps.types.string_model.sdv import StringModelSdv
from exactly_lib.util.symbol_table import SymbolTable
from . import ddvs


class ConstantStringStringModelSdv(StringModelSdv):
    def __init__(self, string: StringSdv):
        self._string = string

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._string.references

    def resolve(self, symbols: SymbolTable) -> StringModelDdv:
        return ddvs.ConstantStringStringModelDdv(self._string.resolve(symbols))


class PathStringModelSdv(StringModelSdv):
    def __init__(self, path: PathSdv):
        self._path = path

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._path.references

    def resolve(self, symbols: SymbolTable) -> StringModelDdv:
        return ddvs.PathStringModelDdv(self._path.resolve(symbols))
