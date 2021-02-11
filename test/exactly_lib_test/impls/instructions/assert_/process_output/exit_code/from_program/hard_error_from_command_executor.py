import unittest

from exactly_lib.impls.os_services import os_services_access
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.impls.instructions.assert_.process_output.exit_code.test_resources.abstract_syntax import \
    InstructionArguments
from exactly_lib_test.impls.instructions.assert_.process_output.exit_code.test_resources.instruction_check import \
    CHECKER
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import ExecutionExpectation, \
    Expectation2
from exactly_lib_test.impls.instructions.test_resources.instr_arr_exp import ParseExpectation
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_case.result.test_resources import pfh_assertions as asrt_pfh
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct2, ProcessExecutionArrangement
from exactly_lib_test.test_case.test_resources.command_executors import CommandExecutorThatRaisesHardError
from exactly_lib_test.type_val_deps.types.test_resources.integer_matcher import \
    IntegerMatcherSymbolContext
from exactly_lib_test.type_val_deps.types.test_resources.program import ProgramSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestTransformationsAssociatedWithTheProgramShouldNotBeApplied(),
    ])


class TestTransformationsAssociatedWithTheProgramShouldNotBeApplied(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        program_symbol = ProgramSymbolContext.of_arbitrary_value('PROGRAM_SYMBOL')
        const_true_int_matcher_symbol = IntegerMatcherSymbolContext.of_primitive_constant(
            'CONST_TRUE_INT_MATCHER',
            result=True,
        )
        all_symbols = [program_symbol,
                       const_true_int_matcher_symbol,
                       ]
        hard_error_message = 'the err msg'
        # ACT & ASSERT #
        CHECKER.check__abs_stx(
            self,
            InstructionArguments(
                program_symbol.abstract_syntax,
                const_true_int_matcher_symbol.abstract_syntax,
            ),
            ArrangementPostAct2(
                symbols=SymbolContext.symbol_table_of_contexts(all_symbols),
                process_execution=ProcessExecutionArrangement(
                    os_services_access.new_for_cmd_exe(
                        CommandExecutorThatRaisesHardError(
                            asrt_text_doc.new_single_string_text_for_test(hard_error_message)
                        ),
                    ),
                ),
            ),
            Expectation2(
                ParseExpectation(
                    symbol_usages=SymbolContext.usages_assertion_of_contexts(all_symbols),
                ),
                ExecutionExpectation(
                    main_result=asrt_pfh.is_hard_error(
                        asrt_text_doc.is_string_for_test_that_equals(hard_error_message)
                    )
                ),
            )
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
