from enum import Enum
from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import TestCaseInstructionWithSymbols
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.test_case.result import svh
from exactly_lib.test_case.result.sh import SuccessOrHardError


class PreviousPhase(Enum):
    SETUP = 1
    ACT = 2
    BEFORE_ASSERT = 3
    ASSERT = 4


class CleanupPhaseInstruction(TestCaseInstructionWithSymbols):
    """
    Abstract base class for instructions of the CLEANUP phase.
    """

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        """
        :raises: :class:`HardErrorException`
        """
        return svh.new_svh_success()

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices,
             previous_phase: PreviousPhase) -> SuccessOrHardError:
        """
        :param previous_phase: The phase that was executed directly before the cleanup phase.
        :raises: :class:`HardErrorException`
        """
        raise NotImplementedError()


def get_symbol_usages(instruction: CleanupPhaseInstruction) -> Sequence[SymbolUsage]:
    return instruction.symbol_usages()
