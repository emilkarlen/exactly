import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.assert_.utils import instruction_from_parts
from exactly_lib.instructions.multi_phase_instructions.utils.instruction_parts import \
    InstructionPartsParser
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case import phase_identifier
from exactly_lib_test.instructions.assert_.test_resources.configuration import AssertConfigurationBase
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.multi_phase_instructions.instruction_integration_test_resources import \
    instruction_from_parts_that_executes_sub_process as test_impl
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check
from exactly_lib_test.test_case_utils.test_resources import svh_assertions
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class ConfigurationForTheAssertPhase(AssertConfigurationBase, test_impl.Configuration):
    def phase(self) -> phase_identifier.Phase:
        return phase_identifier.ASSERT

    def instruction_setup(self) -> SingleInstructionSetup:
        raise ValueError('this method is not used by these tests')

    def instruction_from_parts_parser(self, parts_parser: InstructionPartsParser) -> InstructionParser:
        return instruction_from_parts.Parser(parts_parser)

    def expectation_for_non_zero_exitcode(self) -> Expectation:
        return Expectation(main_result=pfh_check.is_fail())

    def expectation_for_zero_exitcode(self) -> Expectation:
        return Expectation(main_result=pfh_check.is_pass())

    def expect_failing_validation_post_setup(self,
                                             assertion_on_error_message: asrt.ValueAssertion = asrt.anything_goes()):
        return Expectation(validation_post_sds=svh_assertions.is_validation_error(assertion_on_error_message))

    def expect_hard_error_in_main(self) -> Expectation:
        return Expectation(main_result=pfh_check.is_hard_error())


def suite() -> unittest.TestSuite:
    return test_impl.suite_for(ConfigurationForTheAssertPhase())


def run_suite():
    unittest.TextTestRunner().run(suite())


if __name__ == '__main__':
    run_suite()
