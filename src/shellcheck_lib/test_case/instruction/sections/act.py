from shellcheck_lib.document.model import Instruction
from shellcheck_lib.script_language import act_script_management
from shellcheck_lib.test_case.instruction.result.sh import SuccessOrHardError
from shellcheck_lib.test_case.instruction.result.svh import SuccessOrValidationErrorOrHardError
from shellcheck_lib.test_case.instruction.common import GlobalEnvironmentForPostEdsPhase


class PhaseEnvironmentForScriptGeneration:
    """
    The phase-environment for phases that generate a script.
    """

    def __init__(self,
                 script_source_accumulator: act_script_management.ScriptSourceAccumulator):
        self.__script_source_accumulator = script_source_accumulator

    @property
    def append(self) -> act_script_management.ScriptSourceAccumulator:
        return self.__script_source_accumulator


class ActPhaseInstruction(Instruction):
    """
    Abstract base class for instructions of the ACT phase.
    """

    def validate(self,
                 global_environment: GlobalEnvironmentForPostEdsPhase) -> SuccessOrValidationErrorOrHardError:
        raise NotImplementedError()

    def main(self,
             global_environment: GlobalEnvironmentForPostEdsPhase,
             phase_environment: PhaseEnvironmentForScriptGeneration) -> SuccessOrHardError:
        """
        Builds the script, and sets some execution premises (e.g. stdin),
        by updating the phase environment.

        :param global_environment An object passed to all instructions in the Document.
        :param phase_environment An object passed to all instructions in the Phase.
        """
        raise NotImplementedError()
