from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPreEdsStep, GlobalEnvironmentForPostEdsPhase, \
    TestCaseInstruction
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh


class StdinSettings:
    def __init__(self):
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


class SetupPhaseInstruction(TestCaseInstruction):
    """
    Abstract base class for instructions of the SETUP phase.
    """

    def validate_pre_eds(self,
                         environment: GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def validate_post_eds(self,
                          environment: GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             os_services: OsServices,
             environment: GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        raise NotImplementedError()
