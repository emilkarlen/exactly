import unittest
from typing import List

from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.util.file_utils.std import StdOutputFilesContents
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.test_resources.program import ProgramSymbolContext
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import ParseExpectation, Expectation, \
    ExecutionExpectation, arrangement_w_tcds
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as program_args, program_sdvs
from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_syntax as args, \
    model_assertions
from exactly_lib_test.test_case_utils.string_transformers.test_resources import integration_check
from exactly_lib_test.test_case_utils.string_transformers.test_resources import \
    model_construction
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt
from exactly_lib_test.test_resources.files.file_structure import File, DirContents
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestExitCodeInterpretation)


class TestExitCodeInterpretation(unittest.TestCase):
    def test_non_zero_exit_code_and_exit_code_is_not_ignored(self):
        self._check(
            StdOutputFilesContents.empty(),
            exit_code_cases=[1, 2, 69],
            ignore_exit_code=False,
            execution_expectation=
            ExecutionExpectation(
                is_hard_error=asrt_text_doc.is_any_text()
            )
        )

    def test_exit_code_SHOULD_be_ignored_WHEN_option_for_ignoring_exit_code_is_given(self):
        output = StdOutputFilesContents('the output on stdout', '')
        self._check(
            output,
            exit_code_cases=[0, 1, 2, 7],
            ignore_exit_code=True,
            execution_expectation=
            ExecutionExpectation(
                main_result=model_assertions.model_string_matches(
                    asrt.equals(output.out)
                )
            )
        )

    def _check(self,
               output: StdOutputFilesContents,
               exit_code_cases: List[int],
               ignore_exit_code: bool,
               execution_expectation: ExecutionExpectation,
               ):
        # ARRANGE #

        py_file_rel_opt_conf = rel_opt.conf_rel_any(RelOptionType.REL_TMP)

        for exit_code in exit_code_cases:
            with self.subTest(non_zero_exit_code=exit_code):
                py_file = File('exit-with-hard-coded-exit-code.py',
                               py_programs.py_pgm_with_stdout_stderr_exit_code(
                                   stdout_output=output.out,
                                   stderr_output=output.err,
                                   exit_code=exit_code,
                               ),
                               )

                py_file_conf = py_file_rel_opt_conf.named_file_conf(py_file.name)

                program_symbol = ProgramSymbolContext.of_sdv(
                    'PROGRAM_SYMBOL_NAME',
                    program_sdvs.interpret_py_source_file_that_must_exist(py_file_conf.path_sdv)
                )

                # ACT && ASSERT #

                integration_check.CHECKER.check(
                    self,
                    args.syntax_for_run(
                        program_args.symbol_ref_command_elements(program_symbol.name),
                        ignore_exit_code=ignore_exit_code,
                    ).as_remaining_source,
                    model_construction.arbitrary_model_constructor(),
                    arrangement_w_tcds(
                        symbols=program_symbol.symbol_table,
                        tcds_contents=py_file_rel_opt_conf.populator_for_relativity_option_root(
                            DirContents([py_file])
                        ),
                    ),
                    Expectation(
                        ParseExpectation(
                            source=asrt_source.is_at_end_of_line(1),
                            symbol_references=program_symbol.references_assertion
                        ),
                        execution_expectation,
                    ),
                )