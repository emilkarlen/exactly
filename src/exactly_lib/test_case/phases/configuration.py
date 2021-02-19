import pathlib

from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.tcfs.path_relativity import RelHdsOptionType
from exactly_lib.test_case.phases.act.actor import Actor
from exactly_lib.test_case.phases.common import TestCaseInstruction
from exactly_lib.test_case.result.svh import SuccessOrValidationErrorOrHardError
from exactly_lib.test_case.test_case_status import TestCaseStatus
from exactly_lib.util.name_and_value import NameAndValue


class ConfigurationBuilder:
    def __init__(self,
                 home_case_dir_path: pathlib.Path,
                 home_act_dir_path: pathlib.Path,
                 actor: NameAndValue[Actor],
                 test_case_status: TestCaseStatus = TestCaseStatus.PASS):
        self.__actor = actor
        self.__test_case_status = test_case_status
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
    def hds(self) -> HomeDs:
        return HomeDs(case_dir=self.__hds_dirs[RelHdsOptionType.REL_HDS_CASE],
                      act_dir=self.__hds_dirs[RelHdsOptionType.REL_HDS_ACT])

    @property
    def actor(self) -> NameAndValue[Actor]:
        return self.__actor

    def set_actor(self, x: NameAndValue[Actor]):
        self.__actor = x


class ConfigurationPhaseInstruction(TestCaseInstruction):
    """
    Abstract base class for instructions of the configuration phase.
    """

    def main(self, configuration_builder: ConfigurationBuilder) -> SuccessOrValidationErrorOrHardError:
        """
        :param configuration_builder Collects the settings set by the instruction.

        :raises: :class:`HardErrorException`
        """
        raise NotImplementedError()
