from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep, TestCaseInstruction
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import svh


class AssertPhaseInstruction(TestCaseInstruction):
    """
    Abstract base class for instructions of the ASSERT phase.
    """

    @property
    def phase(self) -> phase_identifier.Phase:
        return phase_identifier.ASSERT

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        raise NotImplementedError()
