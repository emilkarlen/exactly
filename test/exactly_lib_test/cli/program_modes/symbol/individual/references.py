import itertools
import unittest

from exactly_lib.cli.definitions import exit_codes
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.processing import exit_values
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case import phase_identifier
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.cli_syntax import short_and_long_option_syntax
from exactly_lib.util.collection import intersperse_list
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib_test.cli.program_modes.symbol.individual.test_resources import output
from exactly_lib_test.cli.program_modes.symbol.test_resources import cl_arguments as symbol_args
from exactly_lib_test.cli.program_modes.symbol.test_resources import sym_def_instruction as sym_def
from exactly_lib_test.cli.program_modes.symbol.test_resources.source_type_checks import check_case_and_suite
from exactly_lib_test.cli.program_modes.test_resources.test_with_files_in_tmp_dir import Arrangement
from exactly_lib_test.symbol.test_resources.string import StringSymbolContext
from exactly_lib_test.symbol.test_resources.symbol_syntax import NOT_A_VALID_SYMBOL_NAME
from exactly_lib_test.test_resources.files.file_structure import empty_file, DirContents, File
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as asrt_proc_result
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestInvalidSymbolNameArguments),
        unittest.makeSuite(TestCaseContainsNoSymbolWithTheGivenName),
        unittest.makeSuite(TestSuccessfulScenarios),
    ])


class TestInvalidSymbolNameArguments(unittest.TestCase):
    def test_superfluous_arguments(self):
        case_file = empty_file('test.xly')

        check_case_and_suite(
            self,
            symbol_command_arguments=
            symbol_args.individual__references(
                case_file.name,
                'symbol_name',
            ) + ['superfluous'],
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
        case_file = empty_file('test.xly')

        check_case_and_suite(
            self,
            symbol_command_arguments=
            symbol_args.individual__references(
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
        case_file = empty_file('test.xly')

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

        case_with_single_def = File('test.xly',
                                    lines_content([
                                        phase_names.SETUP.syntax,
                                        sym_def.define_string(name_of_existing_symbol, 'value'),
                                    ]))

        check_case_and_suite(
            self,
            symbol_command_arguments=
            symbol_args.individual__references(
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
    def test_no_references(self):
        name_of_existing_symbol = 'STRING_SYMBOL'

        case_with_single_def = File('test.xly',
                                    lines_content([
                                        phase_names.SETUP.syntax,
                                        sym_def.define_string(name_of_existing_symbol, 'value'),
                                    ]))

        check_case_and_suite(
            self,
            symbol_command_arguments=
            symbol_args.individual__references(
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
            asrt_proc_result.is_result_for_empty_stdout(
                exit_codes.EXIT_OK
            )
        )

    def test_single_reference_not_in_act(self):
        name_of_existing_symbol = 'STRING_SYMBOL'

        reference_source = sym_def.reference_to(name_of_existing_symbol, ValueType.STRING)
        case_with_single_def = File('test.xly',
                                    lines_content([
                                        phase_names.SETUP.syntax,
                                        sym_def.define_string(name_of_existing_symbol, 'value'),

                                        phase_names.ASSERT.syntax,
                                        reference_source,
                                    ]))

        expected_reference_output = output.Reference(
            phase_identifier.ASSERT,
            output.LineInFilePosition(case_with_single_def.name, 4),
            [
                reference_source,
            ]
        )

        check_case_and_suite(
            self,
            symbol_command_arguments=
            symbol_args.individual__references(
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
                stdout=asrt.equals(lines_content(expected_reference_output.output_lines())))
        )

    def test_single_reference_to_builtin_symbol(self):
        name_of_user_defined_symbol = 'USER_DEFINED_SYMBOL'
        builtin_symbol = StringSymbolContext.of_constant('BUILTIN_SYMBOL',
                                                         'builtin string symbol value')

        definition_source = sym_def.define_string(name_of_user_defined_symbol,
                                                  symbol_reference_syntax_for_name(builtin_symbol.name))
        case_with_single_def = File('test.xly',
                                    lines_content([
                                        phase_names.SETUP.syntax,
                                        definition_source,
                                    ]))

        expected_reference_output = output.Reference(
            phase_identifier.SETUP,
            output.LineInFilePosition(case_with_single_def.name, 2),
            [
                definition_source,
            ]
        )

        check_case_and_suite(
            self,
            symbol_command_arguments=
            symbol_args.individual__references(
                case_with_single_def.name,
                builtin_symbol.name,
            ),
            arrangement=
            Arrangement(
                cwd_contents=DirContents([
                    case_with_single_def,
                ]),
                main_program_config=sym_def.main_program_config(
                    builtin_symbols=[
                        sym_def.builtin_symbol(builtin_symbol),
                    ]
                ),
            ),
            expectation=
            asrt_proc_result.sub_process_result(
                exitcode=asrt.equals(exit_codes.EXIT_OK),
                stdout=asrt.equals(lines_content(expected_reference_output.output_lines())))
        )

    def test_single_reference_in_act_phase(self):
        name_of_existing_symbol = 'STRING_SYMBOL'

        reference_source = sym_def.reference_to(name_of_existing_symbol, ValueType.STRING)
        case_with_single_def = File('test.xly',
                                    lines_content([
                                        phase_names.SETUP.syntax,
                                        sym_def.define_string(name_of_existing_symbol, 'value'),

                                        phase_names.ACT.syntax,
                                        reference_source,
                                    ]))

        expected_reference_output = output.Reference(
            phase_identifier.ACT,
            None,
            [
                reference_source,
            ]
        )
        check_case_and_suite(
            self,
            symbol_command_arguments=
            symbol_args.individual__references(
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
                stdout=asrt.equals(lines_content(expected_reference_output.output_lines()))
            )
        )

    def test_references_SHOULD_be_listed_phase_order(self):
        name_of_existing_symbol = 'STRING_SYMBOL'

        reference_source = sym_def.reference_to(name_of_existing_symbol, ValueType.STRING)
        case_with_references = File('test.xly',
                                    lines_content([
                                        phase_names.SETUP.syntax,
                                        sym_def.define_string(name_of_existing_symbol, 'value'),

                                        phase_names.CLEANUP.syntax,
                                        reference_source,

                                        phase_names.ASSERT.syntax,
                                        reference_source,

                                        phase_names.BEFORE_ASSERT.syntax,
                                        reference_source,

                                        phase_names.ACT.syntax,
                                        reference_source,

                                        phase_names.SETUP.syntax,
                                        reference_source,

                                    ]))

        expected_reference_outputs = [
            output.Reference(
                phase_identifier.SETUP,
                output.LineInFilePosition(case_with_references.name, 12),
                [reference_source]
            ),
            output.Reference(
                phase_identifier.ACT,
                None,
                [reference_source]
            ),
            output.Reference(
                phase_identifier.BEFORE_ASSERT,
                output.LineInFilePosition(case_with_references.name, 8),
                [reference_source]
            ),
            output.Reference(
                phase_identifier.ASSERT,
                output.LineInFilePosition(case_with_references.name, 6),
                [reference_source]
            ),
            output.Reference(
                phase_identifier.CLEANUP,
                output.LineInFilePosition(case_with_references.name, 4),
                [reference_source]
            ),
        ]

        expected_output_lines = list(itertools.chain.from_iterable(
            intersperse_list(['', ''],
                             list(map(output.Reference.output_lines,
                                      expected_reference_outputs)))
        )
        )
        check_case_and_suite(
            self,
            symbol_command_arguments=
            symbol_args.individual__references(
                case_with_references.name,
                name_of_existing_symbol,
            ),
            arrangement=
            Arrangement(
                cwd_contents=DirContents([
                    case_with_references,
                ]),
                main_program_config=sym_def.main_program_config(),
            ),
            expectation=
            asrt_proc_result.sub_process_result(
                exitcode=asrt.equals(exit_codes.EXIT_OK),
                stdout=asrt.equals(lines_content(expected_output_lines)))
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
