import pathlib
from enum import Enum

from shellcheck_lib.test_case.sections.common import TestCaseInstruction
from shellcheck_lib.test_case.sections.result.sh import SuccessOrHardError


class ExecutionMode(Enum):
    NORMAL = 0
    SKIPPED = 1
    XFAIL = 2


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


class AnonymousPhaseInstruction(TestCaseInstruction):
    """
    Abstract base class for instructions of the anonymous phase.
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
