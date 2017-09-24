import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.cleanup.utils import instruction_from_parts
from exactly_lib.instructions.multi_phase_instructions.utils.instruction_parts import \
    InstructionPartsParser
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case import phase_identifier
from exactly_lib_test.instructions.cleanup.test_resources.configuration import CleanupConfigurationBase
from exactly_lib_test.instructions.cleanup.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.multi_phase_instructions.instruction_integration_test_resources import \
    instruction_from_parts_that_executes_sub_process as test_impl
from exactly_lib_test.test_case.test_resources import sh_assertions
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return test_impl.suite_for(ConfigurationForTheCleanupPhase())


class ConfigurationForTheCleanupPhase(CleanupConfigurationBase, test_impl.Configuration):
    def phase(self) -> phase_identifier.Phase:
        return phase_identifier.CLEANUP

    def instruction_setup(self) -> SingleInstructionSetup:
        raise ValueError('this method is not used by these tests')

    def instruction_from_parts_parser(self, parts_parser: InstructionPartsParser) -> InstructionParser:
        return instruction_from_parts.Parser(parts_parser)

    def expectation_for_zero_exitcode(self) -> Expectation:
        return Expectation(main_result=sh_assertions.is_success())

    def expectation_for_non_zero_exitcode(self) -> Expectation:
        return Expectation(main_result=sh_assertions.is_hard_error())

    def expect_hard_error_in_main(self) -> Expectation:
        return Expectation(main_result=sh_assertions.is_hard_error())

    def expect_failing_validation_post_setup(self,
                                             assertion_on_error_message: asrt.ValueAssertion = asrt.anything_goes()):
        return Expectation(main_result=sh_assertions.is_hard_error(assertion_on_error_message))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
