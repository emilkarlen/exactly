from shellcheck_lib.document.model import Instruction
from shellcheck_lib.test_case.instruction.result.sh import SuccessOrHardError
from shellcheck_lib.test_case.instruction.common import GlobalEnvironmentForPostEdsPhase, \
    PhaseEnvironmentForInternalCommands


class CleanupPhaseInstruction(Instruction):
    """
    Abstract base class for instructions of the CLEANUP phase.
    """

    def main(self,
             global_environment: GlobalEnvironmentForPostEdsPhase,
             phase_environment: PhaseEnvironmentForInternalCommands) -> SuccessOrHardError:
        """
        Does whatever this instruction should do.
        :param global_environment An object passed to all instructions in the Document.
        :param phase_environment An object passed to all instructions in the Phase.
        """
        raise NotImplementedError()
