import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.cleanup.utils import instruction_from_parts
from exactly_lib.impls.instructions.multi_phase.utils.instruction_parts import \
    InstructionPartsParser
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.test_case import phase_identifier
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.impls.instructions.cleanup.test_resources.configuration import CleanupConfigurationBase
from exactly_lib_test.impls.instructions.cleanup.test_resources.instruction_check import Expectation
from exactly_lib_test.impls.instructions.multi_phase.instruction_integration_test_resources import \
    instruction_from_parts_that_executes_sub_process as test_impl
from exactly_lib_test.test_case.result.test_resources import sh_assertions as asrt_sh
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


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
        return Expectation(main_result=asrt_sh.is_success())

    def expectation_for_non_zero_exitcode(self) -> Expectation:
        return Expectation(main_result=asrt_sh.is_hard_error())

    def expect_hard_error_in_main(self) -> Expectation:
        return Expectation(main_result=asrt_sh.is_hard_error())

    def expect_failing_validation_post_setup(
            self,
            assertion_on_error_message: ValueAssertion[str] = asrt.anything_goes()):
        return Expectation(
            main_result=asrt_sh.is_hard_error(
                asrt_text_doc.is_string_for_test(assertion_on_error_message)
            )
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
