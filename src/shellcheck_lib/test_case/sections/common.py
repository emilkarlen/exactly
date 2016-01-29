import pathlib

from shellcheck_lib.document.model import Instruction
from shellcheck_lib.execution import execution_directory_structure as eds_module
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure, log_phase_dir


class HomeAndEds:
    def __init__(self,
                 home_path: pathlib.Path,
                 eds: eds_module.ExecutionDirectoryStructure):
        self._home_path = home_path
        self._eds = eds

    @property
    def home_dir_path(self) -> pathlib.Path:
        return self._home_path

    @property
    def eds(self) -> eds_module.ExecutionDirectoryStructure:
        return self._eds


class GlobalEnvironmentForPreEdsStep:
    def __init__(self,
                 home_dir: pathlib.Path):
        self.__home_dir = home_dir

    @property
    def home_directory(self) -> pathlib.Path:
        return self.__home_dir


class PhaseLogging:
    def __init__(self,
                 eds: ExecutionDirectoryStructure,
                 phase_identifier: str):
        self._phase_dir_path = log_phase_dir(eds, phase_identifier)

    @property
    def dir_path(self) -> pathlib.Path:
        return self._phase_dir_path


class GlobalEnvironmentForPostEdsPhase(GlobalEnvironmentForPreEdsStep):
    def __init__(self,
                 home_dir: pathlib.Path,
                 eds: ExecutionDirectoryStructure,
                 phase_identifier: str):
        super().__init__(home_dir)
        self.__eds = eds
        self._phase_logging = PhaseLogging(eds, phase_identifier)

    @property
    def execution_directory_structure(self) -> ExecutionDirectoryStructure:
        return self.__eds

    @property
    def eds(self) -> ExecutionDirectoryStructure:
        return self.__eds

    @property
    def home_and_eds(self) -> HomeAndEds:
        return HomeAndEds(self.home_directory,
                          self.eds)

    @property
    def phase_logging(self) -> PhaseLogging:
        return self._phase_logging


class TestCaseInstruction(Instruction):
    pass
