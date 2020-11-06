from typing import Optional, Sequence

from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import TestCaseInstructionWithSymbols
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result import sh, svh
from exactly_lib.type_val_prims.string_model import StringModel


class SetupSettingsBuilder:
    def __init__(self):
        self.__stdin = None

    @property
    def stdin(self) -> Optional[StringModel]:
        return self.__stdin

    @stdin.setter
    def stdin(self, x: Optional[StringModel]):
        self.__stdin = x


def default_settings() -> SetupSettingsBuilder:
    return SetupSettingsBuilder()


class SetupPhaseInstruction(TestCaseInstructionWithSymbols):
    """
    Abstract base class for instructions of the SETUP phase.
    """

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        """
        :raises: :class:`HardErrorException`
        """
        return svh.new_svh_success()

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        """
        :raises: :class:`HardErrorException`
        """
        return svh.new_svh_success()

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        """
        :raises: :class:`HardErrorException`
        """
        return sh.new_sh_success()


def get_symbol_usages(instruction: SetupPhaseInstruction) -> Sequence[SymbolUsage]:
    return instruction.symbol_usages()
