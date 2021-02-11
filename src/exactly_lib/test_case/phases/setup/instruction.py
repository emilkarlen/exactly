from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import TestCaseInstructionWithSymbols
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.test_case.phases.setup.settings_builder import SetupSettingsBuilder
from exactly_lib.test_case.result import sh, svh


class SetupPhaseInstruction(TestCaseInstructionWithSymbols):
    """
    Abstract base class for instructions of the SETUP phase.
    """

    def validate_pre_sds(self, environment: InstructionEnvironmentForPreSdsStep,
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        """
        :raises: :class:`HardErrorException`
        """
        return svh.new_svh_success()

    def validate_post_setup(self, environment: InstructionEnvironmentForPostSdsStep,
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        """
        :raises: :class:`HardErrorException`
        """
        return svh.new_svh_success()

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        """
        :raises: :class:`HardErrorException`
        """
        return sh.new_sh_success()


def get_symbol_usages(instruction: SetupPhaseInstruction) -> Sequence[SymbolUsage]:
    return instruction.symbol_usages()
