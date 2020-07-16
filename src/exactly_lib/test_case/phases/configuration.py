import pathlib
from typing import Optional

from exactly_lib.test_case.actor import Actor
from exactly_lib.test_case.phases.common import TestCaseInstruction
from exactly_lib.test_case.result.sh import SuccessOrHardError
from exactly_lib.test_case.test_case_status import TestCaseStatus
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import RelHdsOptionType


class ConfigurationBuilder:
    def __init__(self,
                 home_case_dir_path: pathlib.Path,
                 home_act_dir_path: pathlib.Path,
                 actor: Actor,
                 timeout_in_seconds: Optional[int] = None,
                 test_case_status: TestCaseStatus = TestCaseStatus.PASS):
        self.__actor = actor
        self.__test_case_status = test_case_status
        self.__timeout_in_seconds = timeout_in_seconds
        self.__hds_dirs = {
            RelHdsOptionType.REL_HDS_CASE: home_case_dir_path,
            RelHdsOptionType.REL_HDS_ACT: home_act_dir_path,
        }

    @property
    def test_case_status(self) -> TestCaseStatus:
        return self.__test_case_status

    def set_test_case_status(self, x: TestCaseStatus):
        self.__test_case_status = x

    def set_hds_dir(self, d: RelHdsOptionType, value: pathlib.Path):
        self.__hds_dirs[d] = value

    def get_hds_dir(self, d: RelHdsOptionType) -> pathlib.Path:
        return self.__hds_dirs[d]

    @property
    def hds(self) -> HomeDirectoryStructure:
        return HomeDirectoryStructure(case_dir=self.__hds_dirs[RelHdsOptionType.REL_HDS_CASE],
                                      act_dir=self.__hds_dirs[RelHdsOptionType.REL_HDS_ACT])

    @property
    def actor(self) -> Actor:
        return self.__actor

    def set_actor(self, x: Actor):
        self.__actor = x

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

    def main(self, configuration_builder: ConfigurationBuilder) -> SuccessOrHardError:
        """
        :param configuration_builder Collects the settings set by the instruction.
        """
        raise NotImplementedError()
