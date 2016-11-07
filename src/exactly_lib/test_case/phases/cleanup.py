from enum import Enum

from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep, TestCaseInstruction
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case.phases.result.sh import SuccessOrHardError


class PreviousPhase(Enum):
    SETUP = 1
    BEFORE_ASSERT = 2
    ASSERT = 3


class CleanupPhaseInstruction(TestCaseInstruction):
    """
    Abstract base class for instructions of the CLEANUP phase.
    """

    @property
    def phase(self) -> phase_identifier.Phase:
        return phase_identifier.CLEANUP

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             previous_phase: PreviousPhase,
             os_services: OsServices) -> SuccessOrHardError:
        """
        :param previous_phase: The phase that was executed directly before the cleanup phase.
        """
        raise NotImplementedError()
