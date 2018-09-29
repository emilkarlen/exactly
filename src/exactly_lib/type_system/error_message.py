from exactly_lib.test_case_file_structure import sandbox_directory_structure as _sds
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.util.symbol_table import SymbolTable


class ErrorMessageResolvingEnvironment:
    def __init__(self,
                 tcds: HomeAndSds,
                 symbols: SymbolTable = None):
        self._tcds = tcds
        self._symbols = SymbolTable() if symbols is None else symbols

    @property
    def tcds(self) -> HomeAndSds:
        return self._tcds

    @property
    def sds(self) -> _sds.SandboxDirectoryStructure:
        return self._tcds.sds

    @property
    def symbols(self) -> SymbolTable:
        return self._symbols
