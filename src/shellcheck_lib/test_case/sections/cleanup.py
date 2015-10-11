from shellcheck_lib.document.model import Instruction
from shellcheck_lib.test_case.sections.result.sh import SuccessOrHardError
from shellcheck_lib.test_case.instruction.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.os_services import OsServices


class CleanupPhaseInstruction(Instruction):
    """
    Abstract base class for instructions of the CLEANUP phase.
    """

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> SuccessOrHardError:
        raise NotImplementedError()
