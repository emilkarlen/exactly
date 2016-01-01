from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase, TestCaseInstruction
from shellcheck_lib.test_case.sections.result.sh import SuccessOrHardError


class CleanupPhaseInstruction(TestCaseInstruction):
    """
    Abstract base class for instructions of the CLEANUP phase.
    """

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> SuccessOrHardError:
        raise NotImplementedError()
