import datetime
import pathlib
import unittest

from exactly_lib.processing import processors as case_processing
from exactly_lib.processing import test_case_processing
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.processing.preprocessor import IDENTITY_PREPROCESSOR
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.test_suite import execution
from exactly_lib.test_suite import exit_values
from exactly_lib.test_suite.reporters import simple_progress_reporter as sut
from exactly_lib.util.string import lines_content
from exactly_lib_test.execution.test_resources.act_source_executor import \
    ActSourceAndExecutorConstructorThatRunsConstantActions
from exactly_lib_test.test_resources.str_std_out_files import StringStdOutFiles
from exactly_lib_test.test_suite.test_resources.execution_utils import TestCaseProcessorThatGivesConstant, \
    FULL_RESULT_PASS


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestExecutionOfSuite),
        unittest.makeSuite(TestFinalResultFormatting)
    ])


class TestExecutionOfSuite(unittest.TestCase):
    def test_empty_suite_SHOULD_exit_with_success_and_print_single_line_with_ok_identifier(self):
        # ARRANGE #
        factory = sut.SimpleProgressRootSuiteReporterFactory()
        std_output_files = StringStdOutFiles()
        root_file_path = pathlib.Path()
        reporter = factory.new_reporter(std_output_files.stdout_files, root_file_path)
        result = test_case_processing.new_executed(FULL_RESULT_PASS)
        executor = execution.SuitesExecutor(reporter, DEFAULT_CASE_PROCESSING,
                                            TestCaseProcessorThatGivesConstant(result))
        test_suites = []
        # ACT #
        exit_value = executor.execute_and_report(test_suites)
        # ASSERT #
        std_output_files.finish()
        self.assertEquals(exit_values.ALL_PASS, exit_value)
        self.assertEqual(lines_content([exit_values.ALL_PASS.exit_identifier]),
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


DEFAULT_CASE_PROCESSING = case_processing.Configuration(
    lambda x: ((), ()),
    InstructionsSetup({}, {}, {}, {}, {}),
    TestCaseHandlingSetup(ActPhaseSetup(ActSourceAndExecutorConstructorThatRunsConstantActions()),
                          IDENTITY_PREPROCESSOR),
    False)
