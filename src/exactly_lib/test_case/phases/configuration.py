import pathlib

from exactly_lib.execution.execution_mode import ExecutionMode
from exactly_lib.test_case.phases.common import TestCaseInstruction
from exactly_lib.test_case.phases.result.sh import SuccessOrHardError


class ConfigurationBuilder:
    def __init__(self, home_dir_path: pathlib.Path):
        self.__home_dir_path = home_dir_path
        self.__execution_mode = ExecutionMode.NORMAL

    @property
    def execution_mode(self) -> ExecutionMode:
        return self.__execution_mode

    def set_execution_mode(self,
                           x: ExecutionMode):
        self.__execution_mode = x

    @property
    def home_dir(self) -> str:
        return str(self.__home_dir_path)

    @property
    def home_dir_path(self) -> pathlib.Path:
        return self.__home_dir_path

    def set_home_dir(self, x: pathlib.Path):
        self.__home_dir_path = x


class ConfigurationPhaseInstruction(TestCaseInstruction):
    """
    Abstract base class for instructions of the configuration phase.
    """

    def main(self,
             global_environment,
             configuration_builder: ConfigurationBuilder) -> SuccessOrHardError:
        """
        Does whatever this instruction should do.
        :param global_environment An object passed to all instructions in the Document.
        :param configuration_builder An object passed to all instructions in the Phase.
        """
        raise NotImplementedError()
