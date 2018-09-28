import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.assert_.utils import instruction_from_parts
from exactly_lib.instructions.multi_phase.utils.instruction_parts import \
    InstructionPartsParser
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.test_case import phase_identifier
from exactly_lib_test.instructions.assert_.test_resources.configuration import AssertConfigurationBase
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.multi_phase.instruction_integration_test_resources import \
    instruction_from_parts_that_executes_sub_process as test_impl
from exactly_lib_test.test_case.result.test_resources import pfh_assertions, svh_assertions
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    return test_impl.suite_for(ConfigurationForTheAssertPhase())


class ConfigurationForTheAssertPhase(AssertConfigurationBase, test_impl.Configuration):
    def phase(self) -> phase_identifier.Phase:
        return phase_identifier.ASSERT

    def instruction_setup(self) -> SingleInstructionSetup:
        raise ValueError('this method is not used by these tests')

    def instruction_from_parts_parser(self, parts_parser: InstructionPartsParser) -> InstructionParser:
        return instruction_from_parts.Parser(parts_parser)

    def expectation_for_non_zero_exitcode(self) -> Expectation:
        return Expectation(main_result=pfh_assertions.is_fail())

    def expectation_for_zero_exitcode(self) -> Expectation:
        return Expectation(main_result=pfh_assertions.is_pass())

    def expect_failing_validation_post_setup(self,
                                             assertion_on_error_message: ValueAssertion = asrt.anything_goes()):
        return Expectation(validation_post_sds=svh_assertions.is_validation_error(assertion_on_error_message))

    def expect_hard_error_in_main(self) -> Expectation:
        return Expectation(main_result=pfh_assertions.is_hard_error())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
