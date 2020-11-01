import unittest
from typing import List, Callable

from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as args
from exactly_lib_test.test_case_utils.file_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.file_matcher.test_resources.argument_building import PathArgumentPositionArgument
from exactly_lib_test.test_case_utils.matcher.test_resources.run_program import test_cases
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as program_args
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.data.test_resources.symbol_reference_assertions import \
    is_reference_to_data_type_symbol
from exactly_lib_test.type_val_deps.types.test_resources.program import is_reference_to_program


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestPathOfModelFileShouldBeLastArgumentWhenNoOptOrLastOpt(),
        TestPathOfModelFileShouldReplaceMarkerArgumentsWhenMarkerOpt(),
    ])


class TestPathOfModelFileShouldBeLastArgumentWhenNoOptOrLastOpt(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        arg_pos_option_cases = [
            NameAndValue(
                'default',
                args.PathArgumentPositionDefault(),
            ),
            NameAndValue(
                'last',
                args.PathArgumentPositionLast(),
            ),
        ]

        # ACT && ASSERT #

        for arg_pos_option_case in arg_pos_option_cases:
            with self.subTest(arg_pos_option_case.name):
                _check(
                    self,
                    arg_pos_option_case.value,
                    command_line_arguments_cases=[
                        [],
                        ['one'],
                        ['one', 'two'],
                    ],
                    expected_arg_list=expected_arguments_to_program__last,
                )


class TestPathOfModelFileShouldReplaceMarkerArgumentsWhenMarkerOpt(unittest.TestCase):
    def runTest(self):
        marker = 'the_marker'
        not_marker_1 = marker + '1'
        not_marker_2 = marker + '2'

        def expected_arguments_to_program(command_line_arguments: List[str],
                                          model_path: str) -> List[str]:
            return [
                (
                    model_path
                    if arg == marker
                    else
                    arg
                )
                for arg in command_line_arguments
            ]

        _check(
            self,
            args.PathArgumentPositionMarker(marker),
            command_line_arguments_cases=[
                [],
                [not_marker_1],
                [marker],
                [not_marker_1, not_marker_2],
                [marker, not_marker_1, marker, not_marker_2, marker],
            ],
            expected_arg_list=expected_arguments_to_program,
        )


def _check(
        put: unittest.TestCase,
        arg_pos_option: PathArgumentPositionArgument,
        command_line_arguments_cases: List[List[str]],
        expected_arg_list: Callable[[List[str], str], List[str]],
):
    # ARRANGE #

    program_symbol_name = 'PROGRAM_THAT_EXECUTES_PY_FILE'
    command_line_arg_list_symbol_name = 'COMMAND_LINE_ARGUMENTS_LIST'

    model_file_path = 'the-file-to-match'

    # ACT && ASSERT #

    integration_check.CHECKER__PARSE_FULL.check_multi__w_source_variants_for_full_line_parser(
        put,
        args.RunProgram(
            program_args.symbol_ref_command_elements(
                program_symbol_name,
                arguments=[symbol_reference_syntax_for_name(command_line_arg_list_symbol_name)],
            ),
            arg_pos_option,
        ).as_arguments,
        input_=integration_check.constant_relative_file_name(model_file_path),
        symbol_references=asrt.matches_sequence([
            is_reference_to_program(program_symbol_name),
            is_reference_to_data_type_symbol(command_line_arg_list_symbol_name),
        ]),
        execution=[
            test_cases.argument_list_exe_case(
                command_line_arguments,
                expected_arg_list(command_line_arguments, model_file_path),
                program_symbol_name,
                command_line_arg_list_symbol_name)
            for command_line_arguments in command_line_arguments_cases
        ],
    )


def expected_arguments_to_program__last(command_line_arguments: List[str],
                                        model_path: str) -> List[str]:
    return command_line_arguments + [model_path]
