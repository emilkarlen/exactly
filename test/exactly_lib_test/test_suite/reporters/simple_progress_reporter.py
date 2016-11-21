import datetime
import unittest
from pathlib import Path

from exactly_lib.execution import exit_values as case_ev
from exactly_lib.execution import result
from exactly_lib.processing import test_case_processing
from exactly_lib.test_suite import execution
from exactly_lib.test_suite import exit_values as suite_ev
from exactly_lib.test_suite import structure
from exactly_lib.test_suite.execution import SuitesExecutor
from exactly_lib.test_suite.reporters import simple_progress_reporter as sut
from exactly_lib.util.string import lines_content
from exactly_lib_test.test_resources.str_std_out_files import StringStdOutFiles
from exactly_lib_test.test_suite.reporters.test_resources import FULL_RESULT_HARD_ERROR, FULL_RESULT_VALIDATE, \
    FULL_RESULT_IMPLEMENTATION_ERROR
from exactly_lib_test.test_suite.test_resources.execution_utils import TestCaseProcessorThatGivesConstant, \
    FULL_RESULT_PASS, test_suite, DUMMY_CASE_PROCESSING, test_case, FULL_RESULT_FAIL, FULL_RESULT_SKIP


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestExecutionOfSuite),
        unittest.makeSuite(TestFinalResultFormatting)
    ])


def _suite_begin(file_name: str) -> str:
    return 'suite ' + file_name + ': begin'


def _suite_end(file_name: str) -> str:
    return 'suite ' + file_name + ': end'


def _case(file_name: str, exit_value: case_ev.ExitValue) -> str:
    return 'case  ' + file_name + ': ' + exit_value.exit_identifier


class TestExecutionOfSuite(unittest.TestCase):
    def test_single_empty_suite(self):
        # ARRANGE #
        expected_exit_value = suite_ev.ALL_PASS
        expected_output = lines_content([
            _suite_begin('root file name'),
            _suite_end('root file name'),
            expected_exit_value.exit_identifier,
        ])
        root_suite = test_suite('root file name', [], [])
        test_suites = [root_suite]
        std_output_files = StringStdOutFiles()
        executor = _suite_executor_for_case_processing_that_unconditionally(FULL_RESULT_PASS,
                                                                            root_suite,
                                                                            std_output_files,
                                                                            Path())
        # ACT #
        exit_code = executor.execute_and_report(test_suites)
        # ASSERT #
        std_output_files.finish()

        self.assertEquals(expected_exit_value.exit_code, exit_code)
        self.assertEqual(expected_output, std_output_files.stdout_contents)

    def test_suite_with_single_case(self):
        cases = [
            (FULL_RESULT_PASS, case_ev.EXECUTION__PASS, suite_ev.ALL_PASS),
            (FULL_RESULT_FAIL, case_ev.EXECUTION__FAIL, suite_ev.FAILED_TESTS),
            (FULL_RESULT_SKIP, case_ev.EXECUTION__SKIPPED, suite_ev.ALL_PASS),
            (FULL_RESULT_HARD_ERROR, case_ev.EXECUTION__HARD_ERROR, suite_ev.FAILED_TESTS),
            (FULL_RESULT_VALIDATE, case_ev.EXECUTION__VALIDATE, suite_ev.FAILED_TESTS),
            (FULL_RESULT_IMPLEMENTATION_ERROR, case_ev.EXECUTION__IMPLEMENTATION_ERROR, suite_ev.FAILED_TESTS),
        ]
        for case_result, expected_case_exit_value, expected_suite_exit_value in cases:
            with self.subTest(case_result_status=case_result.status,
                              expected_case_exit_value=expected_case_exit_value,
                              expected_suite_exit_value=expected_suite_exit_value):
                # ARRANGE #
                expected_output = lines_content([
                    _suite_begin('root file name'),
                    _case('test case file', expected_case_exit_value),
                    _suite_end('root file name'),
                    expected_suite_exit_value.exit_identifier,
                ])
                root_suite = test_suite('root file name', [], [test_case('test case file')])
                test_suites = [root_suite]
                std_output_files = StringStdOutFiles()
                executor = _suite_executor_for_case_processing_that_unconditionally(case_result,
                                                                                    root_suite,
                                                                                    std_output_files,
                                                                                    Path())
                # ACT #
                exit_code = executor.execute_and_report(test_suites)
                # ASSERT #
                std_output_files.finish()

                self.assertEquals(expected_suite_exit_value.exit_code, exit_code)
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


def _suite_executor_for_case_processing_that_unconditionally(execution_result: result.FullResult,
                                                             root_suite: structure.TestSuite,
                                                             std_output_files: StringStdOutFiles,
                                                             root_file_path: Path) -> SuitesExecutor:
    factory = sut.SimpleProgressRootSuiteReporterFactory()
    root_suite_reporter = factory.new_reporter(root_suite, std_output_files.stdout_files, root_file_path)
    case_result = test_case_processing.new_executed(execution_result)
    return execution.SuitesExecutor(root_suite_reporter, DUMMY_CASE_PROCESSING,
                                    lambda conf: TestCaseProcessorThatGivesConstant(case_result))
