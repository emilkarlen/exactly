import unittest

from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.test_resources.program import NON_EXISTING_SYSTEM_PROGRAM, ProgramSymbolContext
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import ParseExpectation, Expectation, \
    ExecutionExpectation, arrangement_w_tcds
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as program_args, program_sdvs
from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_syntax as args
from exactly_lib_test.test_case_utils.string_transformers.test_resources import integration_check
from exactly_lib_test.test_case_utils.string_transformers.test_resources import \
    model_construction
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt
from exactly_lib_test.test_resources.files.file_structure import File, DirContents
from exactly_lib_test.test_resources.programs import py_programs


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestHardError)


class TestHardError(unittest.TestCase):
    def test_failure_to_execute_program(self):
        # ARRANGE #

        for with_ignored_exit_code in [False, True]:
            with self.subTest(with_ignored_exit_code=with_ignored_exit_code):
                # ACT && ASSERT #

                integration_check.CHECKER.check(
                    self,
                    args.syntax_for_run(
                        program_args.system_program_argument_elements(NON_EXISTING_SYSTEM_PROGRAM),
                        ignore_exit_code=with_ignored_exit_code,
                    ).as_remaining_source,
                    model_construction.arbitrary_model_constructor(),
                    arrangement_w_tcds(),
                    Expectation(
                        ParseExpectation(
                            source=asrt_source.source_is_at_end,
                        ),
                        ExecutionExpectation(
                            is_hard_error=asrt_text_doc.is_any_text()
                        ),
                    ),
                )

    def test_non_zero_exit_code_and_exit_code_is_not_ignored(self):
        # ARRANGE #

        non_zero_exit_codes = [1, 2, 7]
        py_file_rel_opt_conf = rel_opt.conf_rel_any(RelOptionType.REL_TMP)

        for non_zero_exit_code in non_zero_exit_codes:
            with self.subTest(non_zero_exit_code=non_zero_exit_code):
                py_file = File('exit-hard-coded-exit-code.py',
                               py_programs.py_pgm_with_stdout_stderr_exit_code(
                                   '',
                                   '',
                                   exit_code=non_zero_exit_code,
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
                        ignore_exit_code=False,
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
                            source=asrt_source.source_is_at_end,
                            symbol_references=program_symbol.references_assertion
                        ),
                        ExecutionExpectation(
                            is_hard_error=asrt_text_doc.is_any_text()
                        ),
                    ),
                )
