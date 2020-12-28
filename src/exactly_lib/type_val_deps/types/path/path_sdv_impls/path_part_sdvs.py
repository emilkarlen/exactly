from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_deps.types.path import path_ddvs
from exactly_lib.type_val_deps.types.path.path_part_ddv import PathPartDdv
from exactly_lib.type_val_deps.types.path.path_sdv import PathPartSdv
from exactly_lib.type_val_deps.types.string_.string_ddv import StringDdv
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib.util.symbol_table import SymbolTable


class PathPartSdvAsConstantPath(PathPartSdv):
    def __init__(self, file_name: str):
        self._path_part = path_ddvs.constant_path_part(file_name)

    def resolve(self, symbols: SymbolTable) -> PathPartDdv:
        return self._path_part

    @property
    def references(self) -> list:
        return []


class PathPartSdvAsNothing(PathPartSdv):
    def resolve(self, symbols: SymbolTable) -> PathPartDdv:
        return path_ddvs.empty_path_part()

    @property
    def references(self) -> list:
        return []


class PathPartSdvAsStringSdv(PathPartSdv):
    """
    The referenced symbol must not have any dir-dependencies -
    i.e. not contain references (direct or indirect) to PathDdv:s
    that are not absolute.
    """

    def __init__(self, string: StringSdv):
        self._string = string

    def resolve(self, symbols: SymbolTable) -> PathPartDdv:
        string_ddv = self._string.resolve(symbols)
        assert isinstance(string_ddv, StringDdv)
        path_string = string_ddv.value_when_no_dir_dependencies()
        return path_ddvs.constant_path_part(path_string)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._string.references

    def __str__(self):
        return '{}({})'.format(type(self), repr(self._string))
