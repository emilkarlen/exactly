from enum import Enum

from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep, TestCaseInstructionWithSymbols
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import svh


class AssertPhaseInstruction(TestCaseInstructionWithSymbols):
    """
    Abstract base class for instructions of the ASSERT phase.
    """

    @property
    def phase(self) -> phase_identifier.Phase:
        return phase_identifier.ASSERT

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        raise NotImplementedError()


class AssertPhasePurpose(Enum):
    ASSERTION = 1
    BOTH = 2
    HELPER = 3


class WithAssertPhasePurpose:
    """Interface that makes it possible to group assert phase instructions."""

    @property
    def assert_phase_purpose(self) -> AssertPhasePurpose:
        return AssertPhasePurpose.ASSERTION
