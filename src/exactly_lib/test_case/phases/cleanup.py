from enum import Enum
from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep, TestCaseInstructionWithSymbols
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

    @property
    def phase(self) -> phase_identifier.Phase:
        return phase_identifier.CLEANUP

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             previous_phase: PreviousPhase) -> SuccessOrHardError:
        """
        :param previous_phase: The phase that was executed directly before the cleanup phase.
        """
        raise NotImplementedError()


def get_symbol_usages(instruction: CleanupPhaseInstruction) -> Sequence[SymbolUsage]:
    return instruction.symbol_usages()
