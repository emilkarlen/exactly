import pathlib

from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling
from exactly_lib.test_case.phases.common import TestCaseInstruction
from exactly_lib.test_case.phases.result.sh import SuccessOrHardError
from exactly_lib.test_case.test_case_status import ExecutionMode
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure


class ConfigurationBuilder:
    def __init__(self,
                 home_case_dir_path: pathlib.Path,
                 home_act_dir_path: pathlib.Path,
                 act_phase_handling: ActPhaseHandling,
                 timeout_in_seconds: int = None):
        self.__home_case_dir_path = home_case_dir_path
        self.__home_act_dir_path = home_act_dir_path
        self.__act_phase_handling = act_phase_handling
        self.__execution_mode = ExecutionMode.PASS
        self.__timeout_in_seconds = timeout_in_seconds

    @property
    def execution_mode(self) -> ExecutionMode:
        return self.__execution_mode

    def set_execution_mode(self,
                           x: ExecutionMode):
        self.__execution_mode = x

    @property
    def home_case_dir_path(self) -> pathlib.Path:
        return self.__home_case_dir_path

    def set_home_case_dir(self, x: pathlib.Path):
        self.__home_case_dir_path = x

    @property
    def home_act_dir_path(self) -> pathlib.Path:
        return self.__home_act_dir_path

    def set_home_act_dir(self, x: pathlib.Path):
        self.__home_act_dir_path = x

    @property
    def hds(self) -> HomeDirectoryStructure:
        return HomeDirectoryStructure(case_dir=self.home_case_dir_path,
                                      act_dir=self.home_act_dir_path)

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
        self.__timeout_in_seconds = num_seconds


class ConfigurationPhaseInstruction(TestCaseInstruction):
    """
    Abstract base class for instructions of the configuration phase.
    """

    @property
    def phase(self) -> phase_identifier.Phase:
        return phase_identifier.CONFIGURATION

    def main(self, configuration_builder: ConfigurationBuilder) -> SuccessOrHardError:
        """
        :param configuration_builder Collects the settings set by the instruction.
        """
        raise NotImplementedError()
