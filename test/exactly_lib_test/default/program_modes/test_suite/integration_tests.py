import pathlib
import unittest

from exactly_lib.cli import main_program
from exactly_lib.execution.exit_values import NO_EXECUTION__SYNTAX_ERROR, \
    EXECUTION__PASS
from exactly_lib.test_suite import exit_values
from exactly_lib.util.string import lines_content
from exactly_lib_test.default.program_modes.test_suite.test_resources import \
    default_main_program_suite_preprocessing as pre_proc_tests
from exactly_lib_test.default.test_resources.internal_main_program_runner import \
    main_program_runner_with_default_setup__in_same_process
from exactly_lib_test.test_resources.file_structure import DirContents, File
from exactly_lib_test.test_resources.main_program.main_program_check_base import \
    tests_for_setup_without_preprocessor, tests_for_setup_with_preprocessor
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_suite.reporters.test_resources import simple_progress_reporter_output
from exactly_lib_test.test_suite.reporters.test_resources.simple_progress_reporter_test_setup_base import \
    SetupWithReplacementOfVariableOutputWithPlaceholders


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(
        tests_for_setup_without_preprocessor(BASIC_TESTS,
                                             main_program_runner))
    ret_val.addTest(
        tests_for_setup_with_preprocessor(TEST_TEST_SUITE_PREPROCESSING,
                                          main_program_runner))
    return ret_val


def suite_for_running_main_program_internally() -> unittest.TestSuite:
    return suite_for(main_program_runner_with_default_setup__in_same_process())


class InvalidOptions(SetupWithReplacementOfVariableOutputWithPlaceholders):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([File('main.suite', ''), ])

    def additional_arguments(self) -> list:
        return ['--invalid-option-that-should-cause-failure']

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return []

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        return []

    def expected_exit_code(self) -> int:
        return main_program.EXIT_INVALID_USAGE


class EmptySuite(SetupWithReplacementOfVariableOutputWithPlaceholders):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'empty.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('empty.suite', ''),
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / 'empty.suite'),
            expected_line.suite_end(root_path / 'empty.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


class SuiteWithSingleEmptyTestCase(SetupWithReplacementOfVariableOutputWithPlaceholders):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]', 'the.case'])),
            File('the.case', ''),
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.case(root_path / 'the.case', EXECUTION__PASS.exit_identifier),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


class SuiteWithSingleTestCaseWithOnlySectionHeaders(SetupWithReplacementOfVariableOutputWithPlaceholders):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]',
                                              'the.case'])),
            File('the.case',
                 lines_content([
                     '[conf]',
                     '[setup]',
                     '[act]',
                     '[assert]',
                     '[before-assert]',
                     '[cleanup]',
                 ])),
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.case(root_path / 'the.case', EXECUTION__PASS.exit_identifier),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


class SuiteReferenceToNonExistingCaseFile(SetupWithReplacementOfVariableOutputWithPlaceholders):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]',
                                              'non-existing.case'])),
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return []

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return expected_line.summary_for_invalid_suite(root_path, exit_values.INVALID_SUITE)

    def expected_exit_code(self) -> int:
        return exit_values.INVALID_SUITE.exit_code


class SuiteReferenceToNonExistingSuiteFile(SetupWithReplacementOfVariableOutputWithPlaceholders):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[suites]',
                                              'non-existing.suite'])),
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return []

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return expected_line.summary_for_invalid_suite(root_path, exit_values.INVALID_SUITE)

    def expected_exit_code(self) -> int:
        return exit_values.INVALID_SUITE.exit_code


class SuiteWithSingleCaseWithInvalidSyntax(SetupWithReplacementOfVariableOutputWithPlaceholders):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]',
                                              'invalid-syntax.case'])),
            File('invalid-syntax.case',
                 lines_content(['[invalid section]'])),
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.case(root_path / 'invalid-syntax.case', NO_EXECUTION__SYNTAX_ERROR.exit_identifier),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.FAILED_TESTS)

    def expected_exit_code(self) -> int:
        return exit_values.FAILED_TESTS.exit_code


class ComplexSuccessfulSuite(SetupWithReplacementOfVariableOutputWithPlaceholders):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[suites]',
                                              'sub.suite',
                                              '[cases]',
                                              'main.case'])),
            File('main.case', ''),
            File('sub.suite', lines_content(['[suites]',
                                             'sub-sub.suite',
                                             '[cases]',
                                             'sub.case'])),
            File('sub.case', ''),
            File('sub-sub.suite', ''),
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / 'sub-sub.suite'),
            expected_line.suite_end(root_path / 'sub-sub.suite'),

            expected_line.suite_begin(root_path / 'sub.suite'),
            expected_line.case(root_path / 'sub.case', EXECUTION__PASS.exit_identifier),
            expected_line.suite_end(root_path / 'sub.suite'),

            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.case(root_path / 'main.case', EXECUTION__PASS.exit_identifier),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


BASIC_TESTS = [
    InvalidOptions(),
    EmptySuite(),
    SuiteWithSingleEmptyTestCase(),
    SuiteWithSingleTestCaseWithOnlySectionHeaders(),
    SuiteReferenceToNonExistingCaseFile(),
    SuiteReferenceToNonExistingSuiteFile(),
    SuiteWithSingleCaseWithInvalidSyntax(),
    ComplexSuccessfulSuite(),
]

TEST_TEST_SUITE_PREPROCESSING = [
    pre_proc_tests.PreprocessorIsAppliedWithTestCaseFileAsArgument()
]

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite_for_running_main_program_internally())
