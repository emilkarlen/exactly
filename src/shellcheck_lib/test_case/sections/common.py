import pathlib

from shellcheck_lib.document.model import Instruction
from shellcheck_lib.execution import execution_directory_structure as eds_module
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure


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


class GlobalEnvironmentForPostEdsPhase(GlobalEnvironmentForPreEdsStep):
    def __init__(self,
                 home_dir: pathlib.Path,
                 eds: ExecutionDirectoryStructure):
        super().__init__(home_dir)
        self.__eds = eds

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


class TestCaseInstruction(Instruction):
    pass
