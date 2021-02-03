import unittest

from exactly_lib_test.impls.instructions.assert_.process_output.exit_code.test_resources.abstract_syntax import \
    InstructionArguments
from exactly_lib_test.impls.instructions.assert_.process_output.exit_code.test_resources.instruction_check import \
    CHECKER
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import ParseExpectation, \
    ExecutionExpectation, MultiSourceExpectation, Expectation2
from exactly_lib_test.impls.types.program.parse_program.test_resources import pgm_and_args_cases
from exactly_lib_test.impls.types.program.test_resources.stdin_test_setups import MultipleStdinOfProgramTestSetup, \
    SingleStdinOfProgramTestSetup, NoStdinTestSetup, StdinCheckWithProgramWExitCode0ForSuccess
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources.ds_construction import TcdsArrangementPostAct
from exactly_lib_test.test_case.result.test_resources import pfh_assertions as asrt_pfh
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct2
from exactly_lib_test.type_val_deps.types.test_resources.integer_matcher import \
    IntegerMatcherSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestStdinIsGivenToCommandExecutor),
        TestNonEmptyStdinViaExecution(),
    ])


class TestStdinIsGivenToCommandExecutor(unittest.TestCase):
    def test_stdin_is_devnull_WHEN_program_do_not_define_stdin(self):
        # ARRANGE #
        test_setup = NoStdinTestSetup(self, exit_code=0)

        for pgm_and_args_case in pgm_and_args_cases.cases_w_and_wo_argument_list__including_program_reference():
            all_symbols = list(pgm_and_args_case.symbols) + [CONST_TRUE_INT_MATCHER_SYMBOL]
            with self.subTest(pgm_and_args_case.name):
                # ACT & ASSERT #
                CHECKER.check__abs_stx(
                    self,
                    InstructionArguments(
                        pgm_and_args_case.pgm_and_args,
                        CONST_TRUE_INT_MATCHER_SYMBOL.abstract_syntax,
                    ),
                    ArrangementPostAct2(
                        symbols=SymbolContext.symbol_table_of_contexts(all_symbols),
                        process_execution=test_setup.proc_exe_env__w_stdin_check,
                        tcds=TcdsArrangementPostAct(
                            tcds_contents=pgm_and_args_case.tcds,
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

    def test_stdin_is_contents_of_string_source_WHEN_program_defines_single_stdin(self):
        # ARRANGE #
        test_setup = SingleStdinOfProgramTestSetup(self, exit_code=0)

        for pgm_and_args_case in pgm_and_args_cases.cases_w_and_wo_argument_list__including_program_reference():
            all_symbols = list(pgm_and_args_case.symbols) + [CONST_TRUE_INT_MATCHER_SYMBOL]
            with self.subTest(pgm_and_args_case.name):
                # ACT & ASSERT #
                CHECKER.check__abs_stx__source_variants(
                    self,
                    InstructionArguments(
                        test_setup.program_w_stdin_syntax(pgm_and_args_case.pgm_and_args),
                        CONST_TRUE_INT_MATCHER_SYMBOL.abstract_syntax,
                    ),
                    ArrangementPostAct2(
                        symbols=SymbolContext.symbol_table_of_contexts(all_symbols),
                        process_execution=test_setup.proc_exe_env__w_stdin_check,
                        tcds=TcdsArrangementPostAct(
                            tcds_contents=pgm_and_args_case.tcds,
                        ),
                    ),
                    MultiSourceExpectation(
                        symbol_usages=SymbolContext.usages_assertion_of_contexts(all_symbols),
                        execution=ExecutionExpectation(
                            main_result=asrt_pfh.is_pass()
                        ),
                    ),
                )

    def test_stdin_is_concatenation_of_string_sources_WHEN_program_defines_multiple_stdin(self):
        # ARRANGE #
        test_setup = MultipleStdinOfProgramTestSetup(self, exit_code=0)
        all_symbols = [test_setup.program_symbol, CONST_TRUE_INT_MATCHER_SYMBOL]

        # ACT & ASSERT #
        CHECKER.check__abs_stx__source_variants(
            self,
            InstructionArguments(
                test_setup.program_w_stdin_syntax,
                CONST_TRUE_INT_MATCHER_SYMBOL.abstract_syntax,
            ),
            ArrangementPostAct2(
                symbols=SymbolContext.symbol_table_of_contexts(all_symbols),
                process_execution=test_setup.proc_exe_env__w_stdin_check,
            ),
            MultiSourceExpectation(
                symbol_usages=SymbolContext.usages_assertion_of_contexts(all_symbols),
                execution=ExecutionExpectation(
                    main_result=asrt_pfh.is_pass()
                ),
            ),
        )


class TestNonEmptyStdinViaExecution(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        test_setup = StdinCheckWithProgramWExitCode0ForSuccess()
        # ACT & ASSERT #
        CHECKER.check__abs_stx(
            self,
            InstructionArguments(
                test_setup.program_that_checks_stdin__syntax('the contents of stdin'),
                CONST_TRUE_INT_MATCHER_SYMBOL.abstract_syntax,
            ),
            ArrangementPostAct2(
                symbols=CONST_TRUE_INT_MATCHER_SYMBOL.symbol_table,
                tcds=TcdsArrangementPostAct(
                    tcds_contents=test_setup.tcds_contents,
                )
            ),
            Expectation2(
                ParseExpectation(
                    symbol_usages=CONST_TRUE_INT_MATCHER_SYMBOL.usages_assertion,
                ),
                execution=ExecutionExpectation(
                    main_result=asrt_pfh.is_pass()
                ),
            ),
        )


CONST_TRUE_INT_MATCHER_SYMBOL = IntegerMatcherSymbolContext.of_primitive_constant(
    'CONST_TRUE_INT_MATCHER',
    result=True,
)
