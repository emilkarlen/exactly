import unittest

from exactly_lib.cli.definitions import exit_codes
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.processing import exit_values
from exactly_lib.symbol.data import string_sdvs
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.cli_syntax import short_and_long_option_syntax
from exactly_lib.util.string import lines_content
from exactly_lib_test.cli.program_modes.symbol.individual.test_resources.output import definition_of_builtin_symbol
from exactly_lib_test.cli.program_modes.symbol.test_resources import cl_arguments as symbol_args
from exactly_lib_test.cli.program_modes.symbol.test_resources import output
from exactly_lib_test.cli.program_modes.symbol.test_resources import sym_def_instruction as sym_def
from exactly_lib_test.cli.program_modes.symbol.test_resources.source_type_checks import check_case_and_suite
from exactly_lib_test.cli.program_modes.test_resources.test_with_files_in_tmp_dir import Arrangement
from exactly_lib_test.symbol.test_resources.symbol_syntax import NOT_A_VALID_SYMBOL_NAME
from exactly_lib_test.test_resources.files.file_structure import empty_file, DirContents, File
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as asrt_proc_result
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions import value_assertion_str as asrt_str


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestInvalidSymbolNameArguments),
        unittest.makeSuite(TestCaseContainsNoSymbolWithTheGivenName),
        unittest.makeSuite(TestSuccessfulScenarios),
    ])


class TestInvalidSymbolNameArguments(unittest.TestCase):
    def test_superfluous_symbol_name(self):
        case_file = empty_file('test.case')

        check_case_and_suite(
            self,
            symbol_command_arguments=
            [
                case_file.name,
                'symbol_name',
                'superfluous',
            ],
            arrangement=
            Arrangement(
                cwd_contents=DirContents([case_file])
            ),
            expectation=
            asrt_proc_result.is_result_for_empty_stdout(
                exit_codes.EXIT_INVALID_USAGE
            )
        )

    def test_invalid_symbol_name(self):
        case_file = empty_file('test.case')

        check_case_and_suite(
            self,
            symbol_command_arguments=
            symbol_args.individual__definition(
                case_file.name,
                NOT_A_VALID_SYMBOL_NAME,
            ),
            arrangement=
            Arrangement(
                cwd_contents=DirContents([case_file])
            ),
            expectation=
            asrt_proc_result.is_result_for_empty_stdout(
                exit_codes.EXIT_INVALID_USAGE
            )
        )

    def test_invalid_option(self):
        case_file = empty_file('test.case')

        check_case_and_suite(
            self,
            symbol_command_arguments=
            [
                case_file.name,
                'symbol_name',
                short_and_long_option_syntax.long_syntax('invalid'),
            ],
            arrangement=
            Arrangement(
                cwd_contents=DirContents([case_file])
            ),
            expectation=
            asrt_proc_result.is_result_for_empty_stdout(
                exit_codes.EXIT_INVALID_USAGE
            )
        )


class TestCaseContainsNoSymbolWithTheGivenName(unittest.TestCase):
    def test(self):
        name_of_existing_symbol = 'STRING_SYMBOL'
        not_the_name_of_an_existing_symbol = 'NON_EXISTING_SYMBOL'

        case_with_single_def = File('test.case',
                                    lines_content([
                                        phase_names.SETUP.syntax,
                                        sym_def.define_string(name_of_existing_symbol, 'value'),
                                    ]))

        check_case_and_suite(
            self,
            symbol_command_arguments=
            symbol_args.individual__definition(
                case_with_single_def.name,
                not_the_name_of_an_existing_symbol,
            ),
            arrangement=
            Arrangement(
                cwd_contents=DirContents([
                    case_with_single_def,
                ]),
                main_program_config=sym_def.main_program_config(),
            ),
            expectation=
            asrt_proc_result.is_result_for_empty_stdout(
                exit_values.EXECUTION__HARD_ERROR.exit_code
            )
        )


class TestSuccessfulScenarios(unittest.TestCase):
    def test_symbol_without_references(self):
        name_of_existing_symbol = 'STRING_SYMBOL'

        case_with_single_def = File('test.case',
                                    lines_content([
                                        phase_names.SETUP.syntax,
                                        sym_def.define_string(name_of_existing_symbol, 'value'),
                                    ]))

        expected_first_line = output.summary_of_single(output.SymbolSummary(name_of_existing_symbol,
                                                                            ValueType.STRING,
                                                                            num_refs=0))
        check_case_and_suite(
            self,
            symbol_command_arguments=
            symbol_args.individual__definition(
                case_with_single_def.name,
                name_of_existing_symbol,
            ),
            arrangement=
            Arrangement(
                cwd_contents=DirContents([
                    case_with_single_def,
                ]),
                main_program_config=sym_def.main_program_config(),
            ),
            expectation=
            asrt_proc_result.sub_process_result(
                exitcode=asrt.equals(exit_codes.EXIT_OK),
                stdout=asrt_str.first_line(asrt.equals(expected_first_line)))
        )

    def test_symbol_with_reference_to_builtin_symbol(self):
        name_of_existing_builtin_symbol = 'BUILTIN_STRING_SYMBOL'
        name_of_existing_user_defined_symbol = 'USER_DEFINED_STRING_SYMBOL'

        case_with_single_def = File(
            'test.case',
            lines_content([
                phase_names.SETUP.syntax,
                sym_def.define_string(name_of_existing_user_defined_symbol,
                                      symbol_reference_syntax_for_name(name_of_existing_builtin_symbol)),
            ])
        )

        expected_first_line = output.summary_of_single(output.SymbolSummary(name_of_existing_user_defined_symbol,
                                                                            ValueType.STRING,
                                                                            num_refs=0))
        check_case_and_suite(
            self,
            symbol_command_arguments=
            symbol_args.individual__definition(
                case_with_single_def.name,
                name_of_existing_user_defined_symbol,
            ),
            arrangement=
            Arrangement(
                cwd_contents=DirContents([
                    case_with_single_def,
                ]),
                main_program_config=sym_def.main_program_config(
                    builtin_symbols=[sym_def.builtin_symbol(name_of_existing_builtin_symbol,
                                                            string_sdvs.str_constant('the builtin symbol value'))],
                ),
            ),
            expectation=
            asrt_proc_result.sub_process_result(
                exitcode=asrt.equals(exit_codes.EXIT_OK),
                stdout=asrt_str.first_line(asrt.equals(expected_first_line)))
        )

    def test_builtin_symbol(self):
        name_of_existing_builtin_symbol = 'BUILTIN_STRING_SYMBOL'

        case_with_single_def = File(
            'test.case',
            '',
        )

        check_case_and_suite(
            self,
            symbol_command_arguments=
            symbol_args.individual__definition(
                case_with_single_def.name,
                name_of_existing_builtin_symbol,
            ),
            arrangement=
            Arrangement(
                cwd_contents=DirContents([
                    case_with_single_def,
                ]),
                main_program_config=sym_def.main_program_config(
                    builtin_symbols=[sym_def.builtin_symbol(name_of_existing_builtin_symbol,
                                                            string_sdvs.str_constant('the builtin symbol value'))],
                ),
            ),
            expectation=
            asrt_proc_result.sub_process_result(
                exitcode=asrt.equals(exit_codes.EXIT_OK),
                stdout=definition_of_builtin_symbol(name_of_existing_builtin_symbol,
                                                    ValueType.STRING,
                                                    num_refs=0)
            )
        )

    def test_builtin_symbol_with_reference_to_it(self):
        name_of_existing_builtin_symbol = 'BUILTIN_STRING_SYMBOL'

        case_with_single_def = File(
            'test.case',
            lines_content([
                phase_names.SETUP.syntax,
                sym_def.reference_to(name_of_existing_builtin_symbol, ValueType.STRING),
            ])
        )

        check_case_and_suite(
            self,
            symbol_command_arguments=
            symbol_args.individual__definition(
                case_with_single_def.name,
                name_of_existing_builtin_symbol,
            ),
            arrangement=
            Arrangement(
                cwd_contents=DirContents([
                    case_with_single_def,
                ]),
                main_program_config=sym_def.main_program_config(
                    builtin_symbols=[sym_def.builtin_symbol(name_of_existing_builtin_symbol,
                                                            string_sdvs.str_constant('the builtin symbol value'))],
                ),
            ),
            expectation=
            asrt_proc_result.sub_process_result(
                exitcode=asrt.equals(exit_codes.EXIT_OK),
                stdout=definition_of_builtin_symbol(name_of_existing_builtin_symbol,
                                                    ValueType.STRING,
                                                    num_refs=1)
            )
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
