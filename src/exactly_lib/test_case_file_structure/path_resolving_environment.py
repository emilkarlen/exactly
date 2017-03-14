import pathlib

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.symbol_table import SymbolTable


class PathResolvingEnvironment:
    """
    Base class for information needed for resolving paths, outside or inside the SDS.
    """

    def __init__(self, value_definitions: SymbolTable = None):
        self._value_definitions = SymbolTable() if value_definitions is None else value_definitions

    @property
    def value_definitions(self) -> SymbolTable:
        return self._value_definitions


class PathResolvingEnvironmentPreSds(PathResolvingEnvironment):
    def __init__(self,
                 home_dir_path: pathlib.Path,
                 value_definitions: SymbolTable = None):
        super().__init__(value_definitions)
        self._home_dir_path = home_dir_path

    @property
    def home_dir_path(self):
        return self._home_dir_path


class PathResolvingEnvironmentPostSds(PathResolvingEnvironment):
    def __init__(self,
                 sds: SandboxDirectoryStructure,
                 value_definitions: SymbolTable = None):
        super().__init__(value_definitions)
        self._sds = sds

    @property
    def sds(self) -> SandboxDirectoryStructure:
        return self._sds


class PathResolvingEnvironmentPreOrPostSds(PathResolvingEnvironmentPreSds, PathResolvingEnvironmentPostSds):
    def __init__(self,
                 home_and_sds: HomeAndSds,
                 value_definitions: SymbolTable = None):
        PathResolvingEnvironmentPreSds.__init__(self, home_and_sds.home_dir_path, value_definitions)
        PathResolvingEnvironmentPostSds.__init__(self, home_and_sds.sds, value_definitions)
        self._home_and_sds = home_and_sds

    @property
    def home_and_sds(self) -> HomeAndSds:
        return self._home_and_sds
