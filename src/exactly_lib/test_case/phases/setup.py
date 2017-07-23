import pathlib

from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep, \
    TestCaseInstructionWithSymbols
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
    def file_name(self) -> pathlib.Path:
        return self.__stdin_file_name

    @file_name.setter
    def file_name(self, x: pathlib.Path):
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


class SetupPhaseInstruction(TestCaseInstructionWithSymbols):
    """
    Abstract base class for instructions of the SETUP phase.
    """

    @property
    def phase(self) -> phase_identifier.Phase:
        return phase_identifier.SETUP

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
