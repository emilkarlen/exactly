import unittest

from exactly_lib.cli.definitions import exit_codes
from exactly_lib.definitions.formatting import SectionName
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.definitions.test_suite import section_names
from exactly_lib.processing import exit_values
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.string import lines_content
from exactly_lib_test.cli.program_modes.symbol.test_resources import cl_arguments as symbol_args
from exactly_lib_test.cli.program_modes.symbol.test_resources import output
from exactly_lib_test.cli.program_modes.symbol.test_resources import sym_def_instruction as sym_def
from exactly_lib_test.cli.program_modes.symbol.test_resources.suite_file_setup import suite_cases
from exactly_lib_test.cli.program_modes.test_resources import test_with_files_in_tmp_dir
from exactly_lib_test.cli.program_modes.test_resources.test_with_files_in_tmp_dir import Arrangement
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_file, File, empty_dir
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as asrt_proc_result
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingScenarios),
        unittest.makeSuite(TestSuccessfulScenarios),
    ])


class TestFailingScenarios(unittest.TestCase):
    def test_invalid_suite_syntax(self):
        suite_file_contents_with_invalid_syntax = lines_content([
            SectionName('nonExistingSection').syntax,
        ])
        valid_empty_case_file = empty_file('empty-valid.case')

        for suite_case in suite_cases('invalid-syntax.suite'):
            with self.subTest(suite_case.name):
                test_with_files_in_tmp_dir.check(
                    self,
                    command_line_arguments=
                    symbol_args.arguments(
                        suite_case.value.suite_arguments + [valid_empty_case_file.name]
                    ),
                    arrangement=
                    Arrangement(
                        cwd_contents=DirContents([
                            suite_case.value.suite_file(suite_file_contents_with_invalid_syntax),
                            valid_empty_case_file,
                        ])
                    ),
                    expectation=
                    asrt_proc_result.is_result_for_empty_stdout(
                        exit_values.NO_EXECUTION__SYNTAX_ERROR.exit_code
                    )
                )

    def test_invalid_suite_file(self):
        case_file = empty_file('test.case')
        suite_file_name = 'test.suite'

        cases = [
            NameAndValue('file does not exist',
                         []
                         ),
            NameAndValue('file is a directory',
                         [
                             empty_dir(suite_file_name)
                         ]),
        ]
        for case in cases:
            with self.subTest(case.name):
                test_with_files_in_tmp_dir.check(
                    self,
                    command_line_arguments=
                    symbol_args.arguments(
                        symbol_args.explicit_suite_and_case(
                            suite_file_name,
                            case_file.name,
                        )
                    ),
                    arrangement=
                    Arrangement(
                        cwd_contents=DirContents(
                            case.value + [case_file]
                        )
                    ),
                    expectation=
                    asrt_proc_result.is_result_for_empty_stdout(
                        exit_codes.EXIT_INVALID_USAGE
                    )
                )


class TestSuccessfulScenarios(unittest.TestCase):
    def test_empty_files(self):
        empty_suite_file_contents = ''
        valid_empty_case_file = empty_file('empty-valid.case')

        for suite_case in suite_cases('empty.suite'):
            with self.subTest(suite_case.name):
                test_with_files_in_tmp_dir.check(
                    self,
                    command_line_arguments=
                    symbol_args.arguments(
                        suite_case.value.suite_arguments + [valid_empty_case_file.name]
                    ),
                    arrangement=
                    Arrangement(
                        cwd_contents=DirContents([
                            suite_case.value.suite_file(empty_suite_file_contents),
                            valid_empty_case_file,
                        ])
                    ),
                    expectation=
                    asrt_proc_result.is_result_for_empty_stdout(
                        exit_codes.EXIT_OK
                    )
                )

    def test_definition_in_suite_and_case(self):
        symbol_in_suite_name = 'SUITE_SYMBOL'
        symbol_in_case_name = 'CASE_SYMBOL'

        suite_with_single_def = lines_content([
            section_names.CASE__SETUP.syntax,
            sym_def.define_string(symbol_in_suite_name, 'value'),
        ])

        case_with_single_def = File('test.case',
                                    lines_content([
                                        phase_names.SETUP.syntax,
                                        sym_def.define_string(symbol_in_case_name, 'value'),
                                    ]))

        for suite_case in suite_cases('single-definition.suite'):
            with self.subTest(suite_case.name):
                test_with_files_in_tmp_dir.check(
                    self,
                    command_line_arguments=
                    symbol_args.arguments(suite_case.value.suite_arguments + [case_with_single_def.name]),
                    arrangement=
                    Arrangement(
                        cwd_contents=DirContents([
                            suite_case.value.suite_file(suite_with_single_def),
                            case_with_single_def,
                        ]),
                        main_program_config=sym_def.main_program_config(),
                    ),
                    expectation=
                    asrt_proc_result.sub_process_result(
                        exitcode=asrt.equals(exit_codes.EXIT_OK),
                        stdout=asrt.equals(output.list_of([
                            output.SymbolSummary(symbol_in_suite_name, ValueType.STRING, num_refs=0),
                            output.SymbolSummary(symbol_in_case_name, ValueType.STRING, num_refs=0),
                        ])),
                    )
                )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
