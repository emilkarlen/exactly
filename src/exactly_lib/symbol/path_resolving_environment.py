from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.test_case_file_structure.tcds import Tcds
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
                 tcds: Tcds,
                 symbols: SymbolTable = None):
        PathResolvingEnvironmentPreSds.__init__(self, tcds.hds, symbols)
        PathResolvingEnvironmentPostSds.__init__(self, tcds.sds, symbols)
        self._tcds = tcds

    @property
    def tcds(self) -> Tcds:
        return self._tcds
