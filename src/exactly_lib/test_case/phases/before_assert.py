from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep, TestCaseInstructionWithSymbols
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh


class BeforeAssertPhaseInstruction(TestCaseInstructionWithSymbols):
    """
    Abstract base class for instructions of the BEFORE-ASSERT phase.
    """

    @property
    def phase(self) -> phase_identifier.Phase:
        return phase_identifier.BEFORE_ASSERT

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> sh.SuccessOrHardError:
        raise NotImplementedError()
