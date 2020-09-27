from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.tcfs.tcds import TestCaseDs
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
                 hds: HomeDs,
                 symbols: SymbolTable = None):
        super().__init__(symbols)
        self._hds = hds

    @property
    def hds(self) -> HomeDs:
        return self._hds


class PathResolvingEnvironmentPostSds(PathResolvingEnvironment):
    def __init__(self,
                 sds: SandboxDs,
                 symbols: SymbolTable = None):
        super().__init__(symbols)
        self._sds = sds

    @property
    def sds(self) -> SandboxDs:
        return self._sds


class PathResolvingEnvironmentPreOrPostSds(PathResolvingEnvironmentPreSds, PathResolvingEnvironmentPostSds):
    def __init__(self,
                 tcds: TestCaseDs,
                 symbols: SymbolTable = None):
        PathResolvingEnvironmentPreSds.__init__(self, tcds.hds, symbols)
        PathResolvingEnvironmentPostSds.__init__(self, tcds.sds, symbols)
        self._tcds = tcds

    @property
    def tcds(self) -> TestCaseDs:
        return self._tcds
