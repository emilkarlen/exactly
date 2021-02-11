from enum import Enum
from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import TestCaseInstructionWithSymbols
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.test_case.result import pfh, svh


class AssertPhaseInstruction(TestCaseInstructionWithSymbols):
    """
    Abstract base class for instructions of the ASSERT phase.
    """

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        """
        :raises: :class:`HardErrorException`
        """
        return svh.new_svh_success()

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        """
        :raises: :class:`HardErrorException`
        """
        return svh.new_svh_success()

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        """
        :raises: :class:`HardErrorException`
        """
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


def get_symbol_usages(instruction: AssertPhaseInstruction) -> Sequence[SymbolUsage]:
    return instruction.symbol_usages()
