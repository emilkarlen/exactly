from shellcheck_lib.document.model import Instruction
from shellcheck_lib.test_case.act_phase_setup import PhaseEnvironmentForScriptGeneration
from shellcheck_lib.test_case.instruction.result.sh import SuccessOrHardError
from shellcheck_lib.test_case.instruction.result.svh import SuccessOrValidationErrorOrHardError
from shellcheck_lib.test_case.instruction.common import GlobalEnvironmentForPostEdsPhase


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
