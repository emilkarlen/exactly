import unittest
from typing import Sequence

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.assert_.utils import instruction_from_parts
from exactly_lib.impls.instructions.multi_phase.utils.instruction_parts import \
    InstructionPartsParser
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case import phase_identifier
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.impls.instructions.assert_.test_resources.configuration import AssertConfigurationBase
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.impls.instructions.multi_phase.instruction_integration_test_resources import \
    instruction_from_parts_that_executes_sub_process as test_impl
from exactly_lib_test.test_case.result.test_resources import pfh_assertions, svh_assertions
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


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
        return Expectation(main_result=pfh_assertions.is_fail__with_arbitrary_message())

    def expectation_for_zero_exitcode(self) -> Expectation:
        return Expectation(main_result=pfh_assertions.is_pass())

    def expect_failing_validation_post_setup(self,
                                             assertion_on_error_message: Assertion[str] = asrt.anything_goes(),
                                             symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
                                             ):
        return Expectation(
            main_result=pfh_assertions.is_hard_error(
                asrt_text_doc.is_string_for_test(assertion_on_error_message)
            ),
            symbol_usages=symbol_usages,
        )

    def expect_hard_error_in_main(self) -> Expectation:
        return Expectation(main_result=pfh_assertions.is_hard_error__with_arbitrary_message())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
