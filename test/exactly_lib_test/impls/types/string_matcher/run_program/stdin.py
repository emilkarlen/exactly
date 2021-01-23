import unittest

from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, ParseExpectation, \
    ExecutionExpectation, Expectation, MultiSourceExpectation
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__for_expr_parse__s__nsc
from exactly_lib_test.impls.types.program.parse_program.test_resources import pgm_and_args_cases
from exactly_lib_test.impls.types.program.test_resources.stdin_test_setups import MultipleStdinOfProgramTestSetup, \
    SingleStdinOfProgramTestSetup, StdinCheckWithProgramWExitCode0ForSuccess
from exactly_lib_test.impls.types.string_matcher.test_resources import abstract_syntaxes
from exactly_lib_test.impls.types.string_matcher.test_resources import integration_check
from exactly_lib_test.impls.types.string_source.test_resources import model_constructor
from exactly_lib_test.type_val_prims.trace.test_resources import matching_result_assertions as asrt_matching_result


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestStdinIsGivenToCommandExecutor),
        TestNonEmptyStdinViaExecution(),
    ])


class TestStdinIsGivenToCommandExecutor(unittest.TestCase):
    def test_stdin_contains_model_contents_WHEN_program_do_not_define_stdin(self):
        # ARRANGE #
        test_setup = SingleStdinOfProgramTestSetup(self, exit_code=0)

        for pgm_and_args_case in pgm_and_args_cases.cases_w_and_wo_argument_list__including_program_reference():
            with self.subTest(pgm_and_args_case.name):
                # ACT & ASSERT #
                integration_check.CHECKER__PARSE_FULL.check__abs_stx(
                    self,
                    abstract_syntaxes.RunProgramAbsStx(
                        pgm_and_args_case.pgm_and_args,
                    ),
                    model_constructor.of_str(self, test_setup.STRING_SOURCE_CONTENTS),
                    arrangement_w_tcds(
                        symbols=pgm_and_args_case.symbol_table,
                        process_execution=test_setup.proc_exe_env__w_stdin_check,
                        tcds_contents=pgm_and_args_case.tcds,
                    ),
                    Expectation(
                        ParseExpectation(
                            symbol_references=pgm_and_args_case.references_assertion,
                        ),
                        execution=ExecutionExpectation(
                            main_result=asrt_matching_result.matches_value(True)
                        ),
                    )
                )

    def test_stdin_is_concatenation_of_model_and_program_stdin_WHEN_program_defines_single_stdin(self):
        # ARRANGE #
        model_contents = '\n'.join(('the', 'contents', 'of', 'the', 'model'))
        test_setup = SingleStdinOfProgramTestSetup(self, exit_code=0,
                                                   additional_stdin=model_contents)

        for pgm_and_args_case in pgm_and_args_cases.cases_w_and_wo_argument_list__including_program_reference():
            with self.subTest(pgm_and_args_case.name):
                # ACT & ASSERT #
                integration_check.CHECKER__PARSE_FULL.check__abs_stx__std_layouts__mk_source_variants(
                    self,
                    equivalent_source_variants__for_expr_parse__s__nsc,
                    abstract_syntaxes.RunProgramAbsStx(
                        test_setup.program_w_stdin_syntax(pgm_and_args_case.pgm_and_args),
                    ),
                    model_constructor.of_str(self, model_contents),
                    arrangement_w_tcds(
                        symbols=pgm_and_args_case.symbol_table,
                        process_execution=test_setup.proc_exe_env__w_stdin_check,
                        tcds_contents=pgm_and_args_case.tcds,
                    ),
                    MultiSourceExpectation(
                        symbol_references=pgm_and_args_case.references_assertion,
                        execution=ExecutionExpectation(
                            main_result=asrt_matching_result.matches_value(True)
                        ),
                    ),
                )

    def test_stdin_is_concatenation_of_model_and_program_stdin_WHEN_program_defines_multiple_stdin(self):
        # ARRANGE #
        model_contents = '\n'.join(('the', 'contents', 'of', 'the', 'model'))
        test_setup = MultipleStdinOfProgramTestSetup(self, exit_code=0,
                                                     additional_stdin=model_contents)
        # ACT & ASSERT #
        integration_check.CHECKER__PARSE_FULL.check__abs_stx__std_layouts__mk_source_variants(
            self,
            equivalent_source_variants__for_expr_parse__s__nsc,
            abstract_syntaxes.RunProgramAbsStx(
                test_setup.program_w_stdin_syntax,
            ),
            model_constructor.of_str(self, model_contents),
            arrangement_w_tcds(
                symbols=test_setup.program_symbol.symbol_table,
                process_execution=test_setup.proc_exe_env__w_stdin_check,
            ),
            MultiSourceExpectation(
                symbol_references=test_setup.program_symbol.references_assertion,
                execution=ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value(True)
                ),
            ),
        )


class TestNonEmptyStdinViaExecution(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        model_contents = '\n'.join(('the', 'contents', 'of', 'the', 'model'))
        test_setup = StdinCheckWithProgramWExitCode0ForSuccess()
        # ACT & ASSERT #
        integration_check.CHECKER__PARSE_FULL.check__abs_stx(
            self,
            abstract_syntaxes.RunProgramAbsStx(
                test_setup.program_that_checks_stdin__syntax('the contents of stdin',
                                                             model_contents),
            ),
            model_constructor.of_str(self, model_contents),
            arrangement_w_tcds(
                tcds_contents=test_setup.tcds_contents,
            ),
            Expectation(
                execution=ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value(True)
                ),
            ),
        )
