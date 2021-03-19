import unittest

from exactly_lib_test.impls.instructions.assert_.process_output.exit_code.test_resources.abstract_syntax import \
    InstructionArguments
from exactly_lib_test.impls.instructions.assert_.process_output.exit_code.test_resources.instruction_check import \
    CHECKER
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import ExecutionExpectation, \
    Expectation2
from exactly_lib_test.impls.instructions.test_resources.instr_arr_exp import ParseExpectation
from exactly_lib_test.impls.types.integer_matcher.test_resources import validation_cases as im_validation_case
from exactly_lib_test.impls.types.program.test_resources import validation_cases as pgm_validation_cases
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct2
from exactly_lib_test.type_val_deps.types.integer_matcher.test_resources.symbol_context import \
    IntegerMatcherSymbolContext
from exactly_lib_test.type_val_deps.types.program.test_resources.symbol_context import ProgramSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestInvalidProgram(),
        TestInvalidMatcher(),
    ])


class TestInvalidProgram(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        valid_int_matcher_symbol = IntegerMatcherSymbolContext.of_arbitrary_value('VALID_INT_MATCHER')

        for invalid_program_case in pgm_validation_cases.failing_validation_cases():
            all_symbols = list(invalid_program_case.value.symbol_contexts) + [valid_int_matcher_symbol]
            directly_referenced_symbols = [invalid_program_case.value.program_symbol_context, valid_int_matcher_symbol]
            with self.subTest(invalid_program_case.name):
                # ACT & ASSERT #
                CHECKER.check__abs_stx(
                    self,
                    InstructionArguments(
                        invalid_program_case.value.abstract_syntax,
                        valid_int_matcher_symbol.abstract_syntax,
                    ),
                    ArrangementPostAct2(
                        symbols=SymbolContext.symbol_table_of_contexts(all_symbols),
                    ),
                    Expectation2(
                        ParseExpectation(
                            symbol_usages=SymbolContext.usages_assertion_of_contexts(directly_referenced_symbols),
                        ),
                        ExecutionExpectation.validation_corresponding_to__post_sds_as_hard_error(
                            invalid_program_case.value.actual,
                        ),
                    )
                )


class TestInvalidMatcher(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        valid_program_symbol = ProgramSymbolContext.of_arbitrary_value('VALID_PROGRAM')

        for invalid_matcher_case in im_validation_case.failing_validation_cases():
            invalid_matcher_symbol = invalid_matcher_case.value.symbol_context
            all_symbols = [valid_program_symbol, invalid_matcher_symbol]
            with self.subTest(invalid_matcher_case.name):
                # ACT & ASSERT #
                invalid_matcher_symbol = invalid_matcher_case.value.symbol_context
                CHECKER.check__abs_stx(
                    self,
                    InstructionArguments(
                        valid_program_symbol.abstract_syntax,
                        invalid_matcher_symbol.abstract_syntax,
                    ),
                    ArrangementPostAct2(
                        symbols=SymbolContext.symbol_table_of_contexts(all_symbols),
                    ),
                    Expectation2(
                        ParseExpectation(
                            symbol_usages=SymbolContext.usages_assertion_of_contexts(all_symbols)
                        ),
                        ExecutionExpectation.validation_corresponding_to__post_sds_as_hard_error(
                            invalid_matcher_case.value.actual,
                        ),
                    )
                )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
