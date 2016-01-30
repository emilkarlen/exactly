from enum import Enum

from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.phases.common import GlobalEnvironmentForPostEdsPhase, TestCaseInstruction, \
    GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.phases.result import svh
from shellcheck_lib.test_case.phases.result.sh import SuccessOrHardError


class PreviousPhase(Enum):
    SETUP = 1
    BEFORE_ASSERT = 2
    ASSERT = 3


class CleanupPhaseInstruction(TestCaseInstruction):
    """
    Abstract base class for instructions of the CLEANUP phase.
    """

    def validate_pre_eds(self,
                         environment: GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             previous_phase: PreviousPhase,
             os_services: OsServices) -> SuccessOrHardError:
        """
        :param previous_phase: The phase that was executed directly before the cleanup phase.
        """
        raise NotImplementedError()
