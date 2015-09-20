from shellcheck_lib.document.model import Instruction
from shellcheck_lib.test_case.instruction.result.pfh import PassOrFailOrHardError
from shellcheck_lib.test_case.instruction.result.svh import SuccessOrValidationErrorOrHardError
from shellcheck_lib.test_case.instruction.common import GlobalEnvironmentForPostEdsPhase, \
    PhaseEnvironmentForInternalCommands


class AssertPhaseInstruction(Instruction):
    """
    Abstract base class for instructions of the ASSERT phase.
    """

    def validate(self,
                 global_environment: GlobalEnvironmentForPostEdsPhase) -> SuccessOrValidationErrorOrHardError:
        raise NotImplementedError()

    def main(self,
             global_environment: GlobalEnvironmentForPostEdsPhase,
             phase_environment: PhaseEnvironmentForInternalCommands) -> PassOrFailOrHardError:
        """
        Does whatever this instruction should do.
        :param global_environment An object passed to all instructions in the Document.
        :param phase_environment An object passed to all instructions in the Phase.
        """
        raise NotImplementedError()
