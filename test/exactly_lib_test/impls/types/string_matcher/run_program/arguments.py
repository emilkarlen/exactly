import unittest

from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib_test.impls.types.matcher.test_resources.run_program import test_cases
from exactly_lib_test.impls.types.program.test_resources import arguments_building as program_args
from exactly_lib_test.impls.types.string_matcher.test_resources import arguments_building2 as args
from exactly_lib_test.impls.types.string_matcher.test_resources import integration_check
from exactly_lib_test.impls.types.string_source.test_resources import model_constructor
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.data.test_resources.symbol_reference_assertions import \
    is_reference_to_data_type_symbol
from exactly_lib_test.type_val_deps.types.test_resources.program import is_reference_to_program


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

        integration_check.CHECKER__PARSE_FULL.check_multi__w_source_variants_for_full_line_parser(
            self,
            args.RunProgram(
                program_args.symbol_ref_command_elements(
                    program_symbol_name,
                    arguments=[symbol_reference_syntax_for_name(command_line_arg_list_symbol_name)],
                )
            ).as_arguments,
            model_constructor.arbitrary(self),
            symbol_references=asrt.matches_sequence([
                is_reference_to_program(program_symbol_name),
                is_reference_to_data_type_symbol(command_line_arg_list_symbol_name),
            ]),
            execution=[
                test_cases.argument_list_exe_case(command_line_arguments,
                                                  command_line_arguments,
                                                  program_symbol_name,
                                                  command_line_arg_list_symbol_name)
                for command_line_arguments in command_line_arguments_cases
            ],
        )
