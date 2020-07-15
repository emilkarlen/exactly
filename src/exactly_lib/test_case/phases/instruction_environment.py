from typing import Dict

from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds, PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case.phases.tmp_file_spaces import PhaseLoggingPaths
from exactly_lib.test_case_file_structure import sandbox_directory_structure as _sds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.util.file_utils.tmp_file_space import TmpDirFileSpace
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.symbol_table import SymbolTable


class InstructionEnvironmentForPreSdsStep:
    def __init__(self,
                 hds: HomeDirectoryStructure,
                 environ: Dict[str, str],
                 timeout_in_seconds: int = None,
                 symbols: SymbolTable = None):
        self.__hds = hds
        self.__timeout_in_seconds = timeout_in_seconds
        self.__environ = environ
        self.__symbols = SymbolTable() if symbols is None else symbols

    @property
    def hds(self) -> HomeDirectoryStructure:
        return self.__hds

    @property
    def environ(self) -> Dict[str, str]:
        """
        The set of environment variables available to instructions.
        These may be both read and written by instructions.
        """
        return self.__environ

    @property
    def timeout_in_seconds(self) -> int:
        """
        :return: None if no timeout
        """
        return self.__timeout_in_seconds

    @property
    def process_execution_settings(self) -> ProcessExecutionSettings:
        return ProcessExecutionSettings(self.timeout_in_seconds, self.environ)

    @property
    def symbols(self) -> SymbolTable:
        return self.__symbols

    @property
    def path_resolving_environment(self) -> PathResolvingEnvironmentPreSds:
        return PathResolvingEnvironmentPreSds(self.__hds, self.__symbols)


class InstructionEnvironmentForPostSdsStep(InstructionEnvironmentForPreSdsStep):
    def __init__(self,
                 hds: HomeDirectoryStructure,
                 environ: Dict[str, str],
                 sds: _sds.SandboxDirectoryStructure,
                 phase_identifier: str,
                 timeout_in_seconds: int = None,
                 symbols: SymbolTable = None):
        super().__init__(hds, environ, timeout_in_seconds, symbols)
        self.__sds = sds
        self._phase_logging = PhaseLoggingPaths(sds.log_dir, phase_identifier)

    @property
    def sds(self) -> _sds.SandboxDirectoryStructure:
        return self.__sds

    @property
    def tcds(self) -> Tcds:
        return Tcds(self.hds,
                    self.sds)

    @property
    def phase_logging(self) -> PhaseLoggingPaths:
        return self._phase_logging

    @property
    def tmp_file_space(self) -> TmpDirFileSpace:
        return self._phase_logging.space_for_instruction()

    @property
    def path_resolving_environment(self) -> PathResolvingEnvironmentPostSds:
        return PathResolvingEnvironmentPostSds(self.__sds, self.symbols)

    @property
    def path_resolving_environment_pre_or_post_sds(self) -> PathResolvingEnvironmentPreOrPostSds:
        return PathResolvingEnvironmentPreOrPostSds(self.tcds, self.symbols)
