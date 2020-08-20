import unittest

from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.test_resources.program import ProgramSymbolContext
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, ParseExpectation, \
    ExecutionExpectation, Expectation
from exactly_lib_test.test_case_utils.matcher.test_resources.run_program import py_programs, \
    assertions as asrt_run
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as program_args
from exactly_lib_test.test_case_utils.program.test_resources import program_sdvs
from exactly_lib_test.test_case_utils.string_matcher.test_resources import arguments_building2 as args
from exactly_lib_test.test_case_utils.string_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt
from exactly_lib_test.test_resources.files.file_structure import File, DirContents


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestStdinShouldBeEmpty()
    ])


class TestStdinShouldBeEmpty(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        model_contents = '\n'.join(('the', 'contents', 'of', 'the', 'model'))

        py_file = File(
            'stdin-parse_check.py',
            py_programs.pgm_that_exists_with_zero_exit_code_iff_stdin_is_not_expected(
                model_contents
            )
        )

        py_file_rel_opt_conf = rel_opt.conf_rel_any(RelOptionType.REL_TMP)
        py_file_conf = py_file_rel_opt_conf.named_file_conf(py_file.name)

        program_symbol = ProgramSymbolContext.of_sdv(
            'PROGRAM_THAT_EXECUTES_PY_FILE',
            program_sdvs.interpret_py_source_file_that_must_exist(py_file_conf.path_sdv)
        )

        # ACT && ASSERT #

        integration_check.CHECKER.check(
            self,
            args.RunProgram(
                program_args.symbol_ref_command_elements(
                    program_symbol.name,
                    arguments=[],
                )
            ).as_remaining_source,
            integration_check.model_of(model_contents),
            arrangement_w_tcds(
                tcds_contents=py_file_rel_opt_conf.populator_for_relativity_option_root(
                    DirContents([py_file])
                ),
                symbols=program_symbol.symbol_table,
            ),
            Expectation(
                ParseExpectation(
                    source=asrt_source.is_at_end_of_line(1),
                    symbol_references=program_symbol.references_assertion,
                ),
                ExecutionExpectation(
                    main_result=asrt_run.is_result_for_py_interpreter(
                        py_programs.EXIT_CODE_FOR_SUCCESS)
                )
            ),
        )
