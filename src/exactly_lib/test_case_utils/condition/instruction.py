from typing import Sequence

from exactly_lib.symbol.symbol_usage import SymbolUsage
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.result import pfh
from exactly_lib.test_case.result import svh
from exactly_lib.test_case_utils import pfh_exception, svh_exception
from exactly_lib.test_case_utils.condition.comparison_structures import ComparisonHandler


class Instruction(AssertPhaseInstruction):
    """Makes an instruction of a :class:`ComparisonHandler`"""

    def __init__(self,
                 comparison_handler: ComparisonHandler):
        self.comparison_setup = comparison_handler

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self.comparison_setup.references

    def validate_pre_sds(self,
                         environment: i.InstructionEnvironmentForPreSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        return svh_exception.translate_svh_exception_to_svh(
            self.comparison_setup.validate_pre_sds,
            environment.path_resolving_environment)

    def main(self,
             environment: i.InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        return pfh_exception.translate_pfh_exception_to_pfh(
            self.comparison_setup.execute,
            environment.path_resolving_environment_pre_or_post_sds)
