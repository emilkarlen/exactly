from shellcheck_lib.document.model import Instruction
from shellcheck_lib.test_case.sections.result.pfh import PassOrFailOrHardError
from shellcheck_lib.test_case.sections.result.svh import SuccessOrValidationErrorOrHardError
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.os_services import OsServices


class AssertPhaseInstruction(Instruction):
    """
    Abstract base class for instructions of the ASSERT phase.
    """

    def validate(self,
                 global_environment: GlobalEnvironmentForPostEdsPhase) -> SuccessOrValidationErrorOrHardError:
        raise NotImplementedError()

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> PassOrFailOrHardError:
        raise NotImplementedError()
