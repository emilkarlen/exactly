from typing import List

from exactly_lib.symbol.data.list_sdv import ListSdv
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.util.symbol_table import SymbolTable


class DataTypeResolvingHelper:
    def __init__(self,
                 symbols: SymbolTable,
                 tcds: Tcds,
                 ):
        self._symbols = symbols
        self._tcds = tcds

    @property
    def tcds(self) -> Tcds:
        return self._tcds

    @property
    def symbols(self) -> SymbolTable:
        return self._symbols

    def path(self, sdv: PathSdv) -> DescribedPath:
        return sdv.resolve(self._symbols).value_of_any_dependency__d(self._tcds)

    def list(self, sdv: ListSdv) -> List[str]:
        return sdv.resolve(self._symbols).value_of_any_dependency(self._tcds)

    def string(self, sdv: StringSdv) -> str:
        return sdv.resolve(self._symbols).value_of_any_dependency(self._tcds)
