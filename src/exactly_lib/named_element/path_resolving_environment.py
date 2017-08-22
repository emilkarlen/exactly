import pathlib

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.symbol_table import SymbolTable


class PathResolvingEnvironment:
    """
    Base class for information needed for resolving paths, outside or inside the SDS.
    """

    def __init__(self, symbols: SymbolTable = None):
        self._symbols = SymbolTable() if symbols is None else symbols

    @property
    def symbols(self) -> SymbolTable:
        return self._symbols


class PathResolvingEnvironmentPreSds(PathResolvingEnvironment):
    def __init__(self,
                 hds: HomeDirectoryStructure,
                 symbols: SymbolTable = None):
        super().__init__(symbols)
        self._hds = hds

    @property
    def hds(self) -> HomeDirectoryStructure:
        return self._hds

    @property
    def home_dir_path(self) -> pathlib.Path:
        return self._hds.case_dir


class PathResolvingEnvironmentPostSds(PathResolvingEnvironment):
    def __init__(self,
                 sds: SandboxDirectoryStructure,
                 symbols: SymbolTable = None):
        super().__init__(symbols)
        self._sds = sds

    @property
    def sds(self) -> SandboxDirectoryStructure:
        return self._sds


class PathResolvingEnvironmentPreOrPostSds(PathResolvingEnvironmentPreSds, PathResolvingEnvironmentPostSds):
    def __init__(self,
                 home_and_sds: HomeAndSds,
                 symbols: SymbolTable = None):
        PathResolvingEnvironmentPreSds.__init__(self, home_and_sds.hds, symbols)
        PathResolvingEnvironmentPostSds.__init__(self, home_and_sds.sds, symbols)
        self._home_and_sds = home_and_sds

    @property
    def home_and_sds(self) -> HomeAndSds:
        return self._home_and_sds
