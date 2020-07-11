import unittest

from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import is_reference_to_data_type_symbol
from exactly_lib_test.symbol.test_resources.program import is_reference_to_program
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import ParseExpectation
from exactly_lib_test.test_case_utils.matcher.test_resources.run_program import test_cases
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as program_args
from exactly_lib_test.test_case_utils.string_matcher.test_resources import arguments_building2 as args
from exactly_lib_test.test_case_utils.string_matcher.test_resources import integration_check
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
            integration_check.arbitrary_model(),
            [
                test_cases.argument_list_exe_case(command_line_arguments,
                                                  command_line_arguments,
                                                  program_symbol_name,
                                                  command_line_arg_list_symbol_name)
                for command_line_arguments in command_line_arguments_cases
            ],
        )