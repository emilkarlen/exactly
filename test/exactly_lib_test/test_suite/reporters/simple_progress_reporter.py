import datetime
import pathlib
import unittest

from exactly_lib.processing import test_case_processing
from exactly_lib.test_suite import execution
from exactly_lib.test_suite import exit_values
from exactly_lib.test_suite.execution import SuitesExecutor
from exactly_lib.test_suite.reporters import simple_progress_reporter as sut
from exactly_lib.util.string import lines_content
from exactly_lib_test.test_resources.str_std_out_files import StringStdOutFiles
from exactly_lib_test.test_suite.test_resources.execution_utils import TestCaseProcessorThatGivesConstant, \
    FULL_RESULT_PASS, new_test_suite, DUMMY_CASE_PROCESSING


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestExecutionOfSuite),
        unittest.makeSuite(TestFinalResultFormatting)
    ])


def _suite_begin(file_name: str):
    return 'suite ' + file_name + ': begin'


def _suite_end(file_name: str):
    return 'suite ' + file_name + ': end'


class TestExecutionOfSuite(unittest.TestCase):
    def test_no_suites_SHOULD_exit_with_success_and_print_single_line_with_ok_identifier(self):
        # ARRANGE #
        test_suites = []
        std_output_files = StringStdOutFiles()
        executor = _suite_executor_for_case_processing_that_unconditionally_passes(std_output_files,
                                                                                   pathlib.Path())
        # ACT #
        exit_value = executor.execute_and_report(test_suites)
        # ASSERT #
        std_output_files.finish()

        self.assertEquals(exit_values.ALL_PASS, exit_value)
        self.assertEqual(lines_content([exit_values.ALL_PASS.exit_identifier]),
                         std_output_files.stdout_contents)

    def test_single_empty_suite_SHOULD_exit_with_success_and_print_suite_lines_and_exit_identifier(self):
        # ARRANGE #
        test_suites = [
            new_test_suite('root-file-name', [], [])
        ]
        std_output_files = StringStdOutFiles()
        executor = _suite_executor_for_case_processing_that_unconditionally_passes(std_output_files,
                                                                                   pathlib.Path())
        # ACT #
        exit_value = executor.execute_and_report(test_suites)
        # ASSERT #
        std_output_files.finish()

        self.assertEquals(exit_values.ALL_PASS, exit_value)
        expected_output = lines_content([
            _suite_begin('root-file-name'),
            _suite_end('root-file-name'),
            exit_values.ALL_PASS.exit_identifier
        ])
        self.assertEqual(expected_output,
                         std_output_files.stdout_contents)


class TestFinalResultFormatting(unittest.TestCase):
    def test_with_no_errors(self):
        # ARRANGE #
        elapsed_time = datetime.timedelta(seconds=1)
        num_test_cases = 5
        errors = {}
        # ACT #
        actual_lines = sut.format_final_result_for_valid_suite(num_test_cases, elapsed_time, errors)
        # ASSERT #
        self._assert_at_least_one_line_was_generated(actual_lines)
        self._assert_line_is_number_of_executed_tests_line(actual_lines[0], num_test_cases)
        self.assertListEqual(actual_lines[1:],
                             [],
                             'Lines after "Ran ..."')

    def test_with_multiple_errors(self):
        # ARRANGE #
        elapsed_time = datetime.timedelta(seconds=1)
        num_test_cases = 6
        errors = {'identifier_4': 4,
                  'longer_identifier_12': 12,
                  }
        # ACT #
        actual_lines = sut.format_final_result_for_valid_suite(num_test_cases, elapsed_time, errors)
        # ASSERT #
        self._assert_at_least_one_line_was_generated(actual_lines)
        self._assert_line_is_number_of_executed_tests_line(actual_lines[0], num_test_cases)
        self.assertListEqual(['',
                              'identifier_4         : 4',
                              'longer_identifier_12 : 12',
                              ],
                             actual_lines[1:],
                             'Lines after "Ran ..."')

    def _assert_at_least_one_line_was_generated(self, actual_lines):
        if not actual_lines:
            self.fail('No lines at all was generated')

    def _assert_line_is_number_of_executed_tests_line(self, line: str, num_cases: int) -> str:
        reg_ex = '^Ran %d tests in .*' % num_cases
        self.assertRegex(line,
                         reg_ex,
                         'Line that reports number of tests and elapsed time')


def _suite_executor_for_case_processing_that_unconditionally_passes(std_output_files: StringStdOutFiles,
                                                                    root_file_path: pathlib.Path) -> SuitesExecutor:
    factory = sut.SimpleProgressRootSuiteReporterFactory()
    root_suite_reporter = factory.new_reporter(std_output_files.stdout_files, root_file_path)
    result = test_case_processing.new_executed(FULL_RESULT_PASS)
    return execution.SuitesExecutor(root_suite_reporter, DUMMY_CASE_PROCESSING,
                                    lambda conf: TestCaseProcessorThatGivesConstant(result))
