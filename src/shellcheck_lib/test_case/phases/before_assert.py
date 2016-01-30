from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.phases.common import GlobalEnvironmentForPostEdsPhase, TestCaseInstruction, \
    GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.phases.result import sh
from shellcheck_lib.test_case.phases.result import svh


class BeforeAssertPhaseInstruction(TestCaseInstruction):
    """
    Abstract base class for instructions of the BEFORE-ASSERT phase.
    """

    def validate_pre_eds(self,
                         environment: GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def validate_post_setup(self,
                            environment: GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> sh.SuccessOrHardError:
        raise NotImplementedError()
