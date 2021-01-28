import unittest

from exactly_lib.util.parse.token import QuoteType
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, ParseExpectation, \
    Expectation, MultiSourceExpectation
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__for_expr_parse__s__nsc
from exactly_lib_test.impls.types.program.parse_program.test_resources import pgm_and_args_cases
from exactly_lib_test.impls.types.program.test_resources.stdin_test_setups import MultipleStdinOfProgramTestSetup, \
    SingleStdinOfProgramTestSetup, NoStdinTestSetup, StdinCheckViaCopyToOutputFileTestSetup
from exactly_lib_test.impls.types.string_source.test_resources import abstract_syntaxes as string_source_abs_stx
from exactly_lib_test.impls.types.string_source.test_resources import integration_check
from exactly_lib_test.impls.types.string_source.test_resources.abstract_syntaxes import StringSourceOfProgramAbsStx
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntaxes import FullProgramAbsStx
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_string_source
from exactly_lib_test.type_val_prims.string_source.test_resources import contents_assertions as asrt_contents


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestStdinIsGivenToCommandExecutor),
        TestStdinViaExecution(),
    ])


class TestStdinIsGivenToCommandExecutor(unittest.TestCase):
    def test_stdin_is_devnull_WHEN_program_do_not_define_stdin(self):
        # ARRANGE #
        test_setup = NoStdinTestSetup(self, exit_code=0)

        for output_file in ProcOutputFile:
            for pgm_and_args_case in pgm_and_args_cases.cases_w_and_wo_argument_list__including_program_reference():
                for ignore_exit_code in [False, True]:
                    with self.subTest(output_file=output_file,
                                      program=pgm_and_args_case.name,
                                      ignore_exit_code=ignore_exit_code):
                        # ACT & ASSERT #
                        CHECKER.check__abs_stx__wo_input(
                            self,
                            StringSourceOfProgramAbsStx(
                                output_file,
                                pgm_and_args_case.pgm_and_args,
                                ignore_exit_code,
                            ),
                            arrangement_w_tcds(
                                symbols=pgm_and_args_case.symbol_table,
                                process_execution=test_setup.proc_exe_env__w_stdin_check,
                                tcds_contents=pgm_and_args_case.tcds,
                            ),
                            Expectation.of_prim__const(
                                parse=ParseExpectation(
                                    symbol_references=pgm_and_args_case.references_assertion,
                                ),
                                primitive=IS_EMPTY_STRING_SOURCE,
                            )
                        )

    def test_stdin_is_contents_of_string_source_WHEN_program_defines_single_stdin(self):
        # ARRANGE #
        test_setup = SingleStdinOfProgramTestSetup(self, exit_code=0)

        for output_file in ProcOutputFile:
            for pgm_and_args_case in pgm_and_args_cases.cases_w_and_wo_argument_list__including_program_reference():
                for ignore_exit_code in [False, True]:
                    with self.subTest(output_file=output_file,
                                      program=pgm_and_args_case.name,
                                      ignore_exit_code=ignore_exit_code):
                        # ACT & ASSERT #
                        CHECKER.check__abs_stx__layouts__source_variants__wo_input(
                            self,
                            equivalent_source_variants__for_expr_parse__s__nsc,
                            StringSourceOfProgramAbsStx(
                                output_file,
                                test_setup.program_w_stdin_syntax(pgm_and_args_case.pgm_and_args),
                                ignore_exit_code,
                            ),
                            arrangement_w_tcds(
                                symbols=pgm_and_args_case.symbol_table,
                                process_execution=test_setup.proc_exe_env__w_stdin_check,
                                tcds_contents=pgm_and_args_case.tcds,
                            ),
                            MultiSourceExpectation.of_prim__const(
                                symbol_references=pgm_and_args_case.references_assertion,
                                primitive=IS_EMPTY_STRING_SOURCE,
                            ),
                        )

    def test_stdin_is_concatenation_of_string_sources_WHEN_program_defines_multiple_stdin(self):
        # ARRANGE #
        test_setup = MultipleStdinOfProgramTestSetup(self, exit_code=0)
        # ACT & ASSERT #
        for output_file in ProcOutputFile:
            for ignore_exit_code in [False, True]:
                with self.subTest(output_file=output_file,
                                  ignore_exit_code=ignore_exit_code):
                    CHECKER.check__abs_stx__layouts__source_variants__wo_input(
                        self,
                        equivalent_source_variants__for_expr_parse__s__nsc,
                        StringSourceOfProgramAbsStx(
                            output_file,
                            test_setup.program_w_stdin_syntax,
                            ignore_exit_code,
                        ),
                        arrangement_w_tcds(
                            symbols=test_setup.program_symbol.symbol_table,
                            process_execution=test_setup.proc_exe_env__w_stdin_check,
                        ),
                        MultiSourceExpectation.of_prim__const(
                            symbol_references=test_setup.program_symbol.references_assertion,
                            primitive=IS_EMPTY_STRING_SOURCE,
                        ),
                    )


class TestStdinViaExecution(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        model_contents = 'the contents of stdin of program'
        stdin_string_source_syntax = string_source_abs_stx.StringSourceOfStringAbsStx.of_str(model_contents,
                                                                                             QuoteType.HARD, )
        for output_file in ProcOutputFile:
            for ignore_exit_code in [False, True]:
                with self.subTest(output_file=output_file,
                                  ignore_exit_code=ignore_exit_code):
                    test_setup = StdinCheckViaCopyToOutputFileTestSetup(output_file)
                    # ACT & ASSERT #
                    CHECKER.check__abs_stx__wo_input(
                        self,
                        StringSourceOfProgramAbsStx(
                            output_file,
                            FullProgramAbsStx(
                                test_setup.program_that_copies_stdin_syntax(),
                                stdin=stdin_string_source_syntax
                            ),
                            ignore_exit_code,
                        ),
                        arrangement_w_tcds(
                            symbols=SymbolContext.symbol_table_of_contexts(test_setup.symbols),
                        ),
                        Expectation.of_prim__const(
                            parse=ParseExpectation(
                                symbol_references=SymbolContext.references_assertion_of_contexts(test_setup.symbols)
                            ),
                            primitive=asrt_string_source.pre_post_freeze__identical(
                                asrt_contents.matches__str(asrt.equals(model_contents))
                            ),
                        ),
                    )


IS_EMPTY_STRING_SOURCE = asrt_string_source.pre_post_freeze__identical(
    asrt_contents.matches__str(asrt.equals(''))
)

CHECKER = integration_check.checker__w_arbitrary_file_relativities()
