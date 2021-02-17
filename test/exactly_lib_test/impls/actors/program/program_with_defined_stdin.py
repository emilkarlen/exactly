import unittest

from exactly_lib.impls.actors.program import actor
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib_test.impls.actors.test_resources import integration_check
from exactly_lib_test.impls.actors.test_resources.integration_check import Arrangement, Expectation, PostSdsExpectation, \
    AtcExeInputArr
from exactly_lib_test.impls.types.program.parse_program.test_resources import pgm_and_args_cases
from exactly_lib_test.impls.types.program.test_resources.stdin_test_setups import \
    StdinCheckViaCopyToOutputFileTestSetup, SingleStdinOfProgramTestSetup, MultipleStdinOfProgramTestSetup
from exactly_lib_test.impls.types.string_source.test_resources import sdvs as ss_sdvs
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources.ds_construction import TcdsArrangementPreAct
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as asrt_proc_result
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestStdinIsGivenToCommandExecutor),
        TestViaExecutionThatStdinShouldBeStdinOfProgramFollowedByStdinOfActExeEnv(),
    ])


class TestStdinIsGivenToCommandExecutor(unittest.TestCase):
    def test_stdin_contains_model_contents_WHEN_program_do_not_define_stdin(self):
        # ARRANGE #
        test_setup = SingleStdinOfProgramTestSetup(self, exit_code=0)

        for pgm_and_args_case in pgm_and_args_cases.cases_w_and_wo_argument_list__including_program_reference():
            with self.subTest(pgm_and_args_case.name):
                # ACT & ASSERT #
                CHECKER.check__abs_stx(
                    self,
                    pgm_and_args_case.pgm_and_args,
                    Arrangement(
                        symbols=pgm_and_args_case.symbol_table,
                        process_execution=test_setup.proc_exe_env__w_stdin_check,
                        atc_exe_input=AtcExeInputArr(
                            stdin_contents=test_setup.STRING_SOURCE_CONTENTS,
                        ),
                        tcds=TcdsArrangementPreAct(
                            tcds_contents=pgm_and_args_case.tcds,
                        ),
                    ),
                    Expectation(
                        symbol_usages=pgm_and_args_case.usages_assertion,
                        post_sds=PostSdsExpectation.constant(
                            sub_process_result_from_execute=asrt_proc_result.matches_proc_result(
                                exit_code=asrt.equals(test_setup.exit_code),
                            )
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
                CHECKER.check__abs_stx(
                    self,
                    test_setup.program_w_stdin_syntax(pgm_and_args_case.pgm_and_args),
                    Arrangement(
                        symbols=pgm_and_args_case.symbol_table,
                        process_execution=test_setup.proc_exe_env__w_stdin_check,
                        atc_exe_input=AtcExeInputArr(
                            stdin_contents=model_contents,
                        ),
                        tcds=TcdsArrangementPreAct(
                            tcds_contents=pgm_and_args_case.tcds,
                        ),
                    ),
                    Expectation(
                        symbol_usages=pgm_and_args_case.usages_assertion,
                        post_sds=PostSdsExpectation.constant(
                            sub_process_result_from_execute=asrt_proc_result.matches_proc_result(
                                exit_code=asrt.equals(test_setup.exit_code),
                            )
                        ),
                    )
                )

    def test_stdin_is_concatenation_of_model_and_program_stdin_WHEN_program_defines_multiple_stdin(self):
        # ARRANGE #
        model_contents = '\n'.join(('the', 'contents', 'of', 'the', 'model'))
        test_setup = MultipleStdinOfProgramTestSetup(self, exit_code=0,
                                                     additional_stdin=model_contents)
        # ACT & ASSERT #
        CHECKER.check__abs_stx(
            self,
            test_setup.program_w_stdin_syntax,
            Arrangement(
                symbols=test_setup.program_symbol.symbol_table,
                process_execution=test_setup.proc_exe_env__w_stdin_check,
                atc_exe_input=AtcExeInputArr(
                    stdin_contents=model_contents,
                ),
                tcds=TcdsArrangementPreAct(),
            ),
            Expectation(
                symbol_usages=test_setup.program_symbol.usages_assertion,
                post_sds=PostSdsExpectation.constant(
                    sub_process_result_from_execute=asrt_proc_result.matches_proc_result(
                        exit_code=asrt.equals(test_setup.exit_code),
                    )
                ),
            )
        )


class TestViaExecutionThatStdinShouldBeStdinOfProgramFollowedByStdinOfActExeEnv(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        stdin_from_act_exe_input = 'the stdin from the Act Execution Input (via [setup])'
        stdin_defined_by_the_program = 'the stdin defined by the program'
        test_setup = StdinCheckViaCopyToOutputFileTestSetup(
            ProcOutputFile.STDOUT,
            stdin_defined_for_program=[
                ss_sdvs.const_str(stdin_defined_by_the_program)
            ]
        )
        full_stdin = stdin_defined_by_the_program + stdin_from_act_exe_input
        # ACT & ASSERT #
        CHECKER.check__abs_stx(
            self,
            test_setup.program_that_copies_stdin_syntax(),
            Arrangement(
                symbols=SymbolContext.symbol_table_of_contexts(test_setup.symbols),
                atc_exe_input=AtcExeInputArr(
                    stdin_contents=stdin_from_act_exe_input,
                ),
                tcds=TcdsArrangementPreAct(),
            ),
            Expectation(
                symbol_usages=SymbolContext.usages_assertion_of_contexts(test_setup.symbols),
                post_sds=PostSdsExpectation.constant(
                    sub_process_result_from_execute=asrt_proc_result.matches_proc_result(
                        exit_code=asrt.equals(0),
                        stdout=asrt.equals(full_stdin)
                    )
                ),
            ),
        )


CHECKER = integration_check.Checker(actor.actor())

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
