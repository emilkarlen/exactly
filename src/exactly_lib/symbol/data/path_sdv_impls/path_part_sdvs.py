from typing import Sequence

from exactly_lib.symbol.data.path_sdv import PathPartSdv
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_system.data import paths
from exactly_lib.type_system.data.path_part import PathPartDdv
from exactly_lib.type_system.data.string_ddv import StringDdv
from exactly_lib.util.symbol_table import SymbolTable


class PathPartSdvAsConstantPath(PathPartSdv):
    def __init__(self, file_name: str):
        self._path_part = paths.constant_path_part(file_name)

    def resolve(self, symbols: SymbolTable) -> PathPartDdv:
        return self._path_part

    @property
    def references(self) -> list:
        return []


class PathPartSdvAsNothing(PathPartSdv):
    def resolve(self, symbols: SymbolTable) -> PathPartDdv:
        return paths.empty_path_part()

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
        return paths.constant_path_part(path_string)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._string.references

    def __str__(self):
        return '{}({})'.format(type(self), repr(self._string))
