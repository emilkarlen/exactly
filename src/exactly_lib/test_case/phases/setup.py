from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep, \
    TestCaseInstruction
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh


class StdinSettings:
    def __init__(self):
        self.__stdin_file_name = None
        self.__stdin_contents = None

    def set_empty(self):
        self.__stdin_file_name = None
        self.__stdin_contents = None

    @property
    def contents(self) -> str:
        return self.__stdin_contents

    @contents.setter
    def contents(self, x: str):
        self.__stdin_file_name = None
        self.__stdin_contents = x

    @property
    def file_name(self) -> str:
        return self.__stdin_file_name

    @file_name.setter
    def file_name(self, x: str):
        self.__stdin_contents = None
        self.__stdin_file_name = x


class SetupSettingsBuilder:
    def __init__(self):
        self.__stdin_settings = StdinSettings()

    @property
    def stdin(self) -> StdinSettings:
        return self.__stdin_settings


def default_settings() -> SetupSettingsBuilder:
    return SetupSettingsBuilder()


class SetupPhaseInstruction(TestCaseInstruction):
    """
    Abstract base class for instructions of the SETUP phase.
    """

    @property
    def phase(self) -> phase_identifier.Phase:
        return phase_identifier.SETUP

    def value_usages(self) -> list:
        """
        Gives information about all value definitions that this instruction uses.

        This list should be available right after construction (and thus should not need
        any phase step to have been executed).

        The list should be in usage order. So, for example, if an instruction defines
        a value X = Y (where Y is a value definition). Then the return value should contain
        an element that says <reference of Y> before the element that says <definition of X>.

        :return: [`ValueUsage`]
        """
        return []

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        return sh.new_sh_success()
