import pathlib

from exactly_lib.execution.act_phase import ActPhaseHandling
from exactly_lib.execution.execution_mode import ExecutionMode
from exactly_lib.test_case.phases.common import TestCaseInstruction
from exactly_lib.test_case.phases.result.sh import SuccessOrHardError


class ConfigurationBuilder:
    def __init__(self,
                 home_dir_path: pathlib.Path,
                 act_phase_handling: ActPhaseHandling,
                 timeout_in_seconds: int = None):
        self.__home_dir_path = home_dir_path
        self.__act_phase_handling = act_phase_handling
        self.__execution_mode = ExecutionMode.NORMAL
        self.__timeout_in_seconds = timeout_in_seconds

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

    @property
    def act_phase_handling(self) -> ActPhaseHandling:
        return self.__act_phase_handling

    def set_act_phase_handling(self, x: ActPhaseHandling):
        self.__act_phase_handling = x

    @property
    def timeout_in_seconds(self) -> int:
        """
        :return: None if no timeout
        """
        return self.__timeout_in_seconds

    def set_timeout_in_seconds(self, num_seconds: int):
        self.__act_phase_handling = num_seconds


class ConfigurationPhaseInstruction(TestCaseInstruction):
    """
    Abstract base class for instructions of the configuration phase.
    """

    def main(self, configuration_builder: ConfigurationBuilder) -> SuccessOrHardError:
        """
        :param configuration_builder Collects the settings set by the instruction.
        """
        raise NotImplementedError()
