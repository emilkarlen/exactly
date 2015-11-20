from shellcheck_lib.document.model import Instruction
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.os_services import OsServices


class AssertPhaseInstruction(Instruction):
    """
    Abstract base class for instructions of the ASSERT phase.
    """

    def validate(self,
                 global_environment: GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        raise NotImplementedError()
