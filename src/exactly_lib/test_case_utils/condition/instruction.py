from exactly_lib.instructions.assert_.utils import return_pfh_via_exceptions
from exactly_lib.instructions.utils import return_svh_via_exceptions
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.result import pfh, svh
from exactly_lib.test_case_utils.condition.comparison_structures import ComparisonHandler


class Instruction(AssertPhaseInstruction):
    """Makes an instruction of a :class:`ComparisonHandler`"""

    def __init__(self,
                 comparison_handler: ComparisonHandler):
        self.comparison_setup = comparison_handler

    def symbol_usages(self) -> list:
        return self.comparison_setup.references

    def validate_pre_sds(self,
                         environment: i.InstructionEnvironmentForPreSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        return return_svh_via_exceptions.translate_svh_exception_to_svh(
            self.comparison_setup.validate_pre_sds,
            environment)

    def main(self,
             environment: i.InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        return return_pfh_via_exceptions.translate_pfh_exception_to_pfh(
            self.comparison_setup.execute,
            environment)
