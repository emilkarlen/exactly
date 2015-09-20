from shellcheck_lib.document.model import Instruction
from shellcheck_lib.test_case.instruction.result.sh import SuccessOrHardError
from shellcheck_lib.test_case.instruction.result.svh import SuccessOrValidationErrorOrHardError
from shellcheck_lib.test_case.instruction.common import GlobalEnvironmentForPreEdsStep, GlobalEnvironmentForPostEdsPhase


class SetupSettingsBuilder:
    def __init__(self,
                 stdin_file_name: str=None):
        self.__stdin_file_name = stdin_file_name

    def set_stdin_file(self,
                       file_name: str):
        self.__stdin_file_name = file_name

    @property
    def stdin_file_name(self) -> str:
        return self.__stdin_file_name

    @stdin_file_name.setter
    def stdin_file_name(self, x: str):
        self.__stdin_file_name = x


class SetupPhaseInstruction(Instruction):
    """
    Abstract base class for instructions of the SETUP phase.
    """

    def pre_validate(self,
                     global_environment: GlobalEnvironmentForPreEdsStep) -> SuccessOrValidationErrorOrHardError:
        raise NotImplementedError()

    def main(self,
             global_environment: GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> SuccessOrHardError:
        """
        Does whatever this instruction should do.
        :param global_environment An object passed to all instructions in the Document.
        """
        raise NotImplementedError()

    def post_validate(self,
                      global_environment: GlobalEnvironmentForPostEdsPhase) -> SuccessOrValidationErrorOrHardError:
        raise NotImplementedError()
