from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase, TestCaseInstruction, \
    GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import svh


class AssertPhaseInstruction(TestCaseInstruction):
    """
    Abstract base class for instructions of the ASSERT phase.
    """

    def validate_pre_eds(self,
                         environment: GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def validate(self,
                 environment: GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        raise NotImplementedError()
