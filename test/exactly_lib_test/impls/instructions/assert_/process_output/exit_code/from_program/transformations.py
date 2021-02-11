import unittest

from exactly_lib.impls.os_services import os_services_access
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
from exactly_lib_test.test_case.test_resources.command_executors import CommandExecutorThatJustReturnsConstant
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntaxes import FullProgramAbsStx
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.symbol_context import \
    StringTransformerSymbolContext
from exactly_lib_test.type_val_deps.types.test_resources.integer_matcher import \
    IntegerMatcherSymbolContext
from exactly_lib_test.type_val_deps.types.test_resources.program import ProgramSymbolContext
from exactly_lib_test.type_val_prims.string_transformer.test_resources.string_transformers import \
    StringTransformerThatFailsTestIfApplied


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
        string_transformer_that_reports_failure_if_applied = StringTransformerSymbolContext.of_primitive(
            'STRING_TRANSFORMER_THAT_MUST_NOT_BE_USED',
            StringTransformerThatFailsTestIfApplied(self)
        )
        all_symbols = [program_symbol,
                       string_transformer_that_reports_failure_if_applied,
                       const_true_int_matcher_symbol,
                       ]
        # ACT & ASSERT #
        CHECKER.check__abs_stx(
            self,
            InstructionArguments(
                FullProgramAbsStx(
                    program_symbol.abstract_syntax,
                    transformation=string_transformer_that_reports_failure_if_applied.abstract_syntax),
                const_true_int_matcher_symbol.abstract_syntax,
            ),
            ArrangementPostAct2(
                symbols=SymbolContext.symbol_table_of_contexts(all_symbols),
                process_execution=ProcessExecutionArrangement(
                    os_services_access.new_for_cmd_exe(
                        CommandExecutorThatJustReturnsConstant(1),
                    ),
                ),
            ),
            Expectation2(
                ParseExpectation(
                    symbol_usages=SymbolContext.usages_assertion_of_contexts(all_symbols),
                ),
                ExecutionExpectation(
                    main_result=asrt_pfh.is_pass()
                ),
            )
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
