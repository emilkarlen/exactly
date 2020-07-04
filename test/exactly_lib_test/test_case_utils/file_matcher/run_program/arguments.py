import unittest
from typing import List

from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTrace
from exactly_lib.type_system.logic.matching_result import MatchingResult
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.data.test_resources.list_ import ListSymbolContext
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import is_reference_to_data_type_symbol
from exactly_lib_test.symbol.test_resources.program import ProgramSymbolContext, is_reference_to_program
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case_utils.file_matcher.run_program.test_resources import is_result_for_py_interpreter
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as args
from exactly_lib_test.test_case_utils.file_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import PrimAndExeExpectation, Arrangement
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import arrangement_w_tcds, \
    ParseExpectation
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as program_args
from exactly_lib_test.test_case_utils.program.test_resources import program_sdvs
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt
from exactly_lib_test.test_resources.files.file_structure import File, DirContents
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestPathOfModelFileShouldBeGivenAsLastArgument()
    ])


class TestPathOfModelFileShouldBeGivenAsLastArgument(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        program_symbol_name = 'PROGRAM_THAT_EXECUTES_PY_FILE'
        command_line_arg_list_symbol_name = 'COMMAND_LINE_ARGUMENTS_LIST'

        model_file_path = 'the-file-to-match'

        command_line_arguments_cases = [
            [],
            ['one'],
            ['one', 'two'],
        ]

        # ACT && ASSERT #

        integration_check.CHECKER.check_multi(
            self,
            args.RunProgram(
                program_args.symbol_ref_command_elements(
                    program_symbol_name,
                    arguments=[symbol_reference_syntax_for_name(command_line_arg_list_symbol_name)],
                )
            ).as_arguments,
            ParseExpectation(
                source=asrt_source.source_is_at_end,
                symbol_references=asrt.matches_sequence([
                    is_reference_to_program(program_symbol_name),
                    is_reference_to_data_type_symbol(command_line_arg_list_symbol_name),
                ]),
            ),
            integration_check.constant_relative_file_name(model_file_path),
            [
                argument_list_case(command_line_arguments,
                                   model_file_path,
                                   program_symbol_name,
                                   command_line_arg_list_symbol_name)
                for command_line_arguments in command_line_arguments_cases
            ],
        )


def expected_arguments_to_program(command_line_arguments: List[str],
                                  model_path: str) -> List[str]:
    return command_line_arguments + [model_path]


def argument_list_case(command_line_arguments: List[str],
                       model_path: str,
                       program_symbol_name: str,
                       list_arg_symbol_name: str,
                       ) -> NExArr[PrimAndExeExpectation[MatcherWTrace[FileMatcherModel], MatchingResult],
                                   Arrangement]:
    expected_arguments = expected_arguments_to_program(command_line_arguments, model_path)

    py_file = File('arguments-checker.py',
                   py_pgm_that_exists_with_zero_exit_code_iff_arguments_are_expected(expected_arguments))

    py_file_rel_opt_conf = rel_opt.conf_rel_any(RelOptionType.REL_TMP)
    py_file_conf = py_file_rel_opt_conf.named_file_conf(py_file.name)

    program_symbol = ProgramSymbolContext.of_sdv(
        program_symbol_name,
        program_sdvs.interpret_py_source_file_that_must_exist(py_file_conf.path_sdv)
    )

    arg_list_symbol = ListSymbolContext.of_constants(
        list_arg_symbol_name,
        command_line_arguments
    )

    return NExArr(
        'Command line arguments: {}. Model path: {}'.format(
            repr(command_line_arguments),
            repr(model_path)
        ),
        PrimAndExeExpectation.of_exe(
            main_result=is_result_for_py_interpreter(EXIT_CODE_FOR_ASSERTION_BY_PY_PROGRAM_SUCCESSFUL)
        ),
        arrangement_w_tcds(
            tcds_contents=py_file_rel_opt_conf.populator_for_relativity_option_root(
                DirContents([py_file])
            ),
            symbols=SymbolContext.symbol_table_of_contexts([
                program_symbol,
                arg_list_symbol,
            ]),
        )
    )


def py_pgm_that_exists_with_zero_exit_code_iff_arguments_are_expected(expected: List[str]) -> str:
    return _PY_PGM_THAT_EXISTS_WITH_ZERO_EXIT_CODE_IFF_ARGUMENTS_ARE_EXPECTED.format(
        expected_arg_list=repr(expected)
    )


EXIT_CODE_FOR_ASSERTION_BY_PY_PROGRAM_SUCCESSFUL = 0

_PY_PGM_THAT_EXISTS_WITH_ZERO_EXIT_CODE_IFF_ARGUMENTS_ARE_EXPECTED = """\
import sys;

expected = {expected_arg_list}

sys.exit(int(expected != sys.argv[1:]))
"""
