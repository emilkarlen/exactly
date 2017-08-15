import unittest

from exactly_lib.instructions.assert_.utils import return_pfh_via_exceptions
from exactly_lib.instructions.assert_.utils.expression.comparison_structures import ComparisonExecutor, \
    ComparisonSetup
from exactly_lib.instructions.utils import return_svh_via_exceptions
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.result import pfh, svh


class Instruction(AssertPhaseInstruction):
    def __init__(self,
                 comparison_setup: ComparisonSetup):
        self.comparison_setup = comparison_setup

    def symbol_usages(self) -> list:
        return self.comparison_setup.references

    def validate_pre_sds(self,
                         environment: i.InstructionEnvironmentForPostSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        return return_svh_via_exceptions.translate_svh_exception_to_svh(
            self.comparison_setup.validate_pre_sds,
            environment)

    def main(self,
             environment: i.InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        return return_pfh_via_exceptions.translate_pfh_exception_to_pfh(
            self._main_that_raises_pfh_exceptions,
            environment,
            os_services)

    def _main_that_raises_pfh_exceptions(self,
                                         environment: i.InstructionEnvironmentForPostSdsStep,
                                         os_services: OsServices):
        lhs = self.comparison_setup.actual_value_lhs.resolve(environment, os_services)
        rhs = self.comparison_setup.integer_resolver.resolve(environment)
        executor = ComparisonExecutor(
            self.comparison_setup.actual_value_lhs.property_name,
            self.comparison_setup.expectation_type,
            lhs,
            rhs,
            self.comparison_setup.operator)
        executor.execute_and_return_pfh_via_exceptions()


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TheSymbolReferences)


class TheSymbolReferences(unittest.TestCase):
    def test_s(self):
        self.fail('todo')
