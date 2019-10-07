import datetime
import os
import re
import unittest
from pathlib import Path

from exactly_lib.common.exit_value import ExitValue
from exactly_lib.execution.full_execution.result import FullExeResult
from exactly_lib.processing import test_case_processing, exit_values as case_ev
from exactly_lib.processing.test_case_processing import test_case_reference_of_source_file
from exactly_lib.test_suite import exit_values as suite_ev
from exactly_lib.test_suite import processing
from exactly_lib.test_suite import structure
from exactly_lib.test_suite.file_reading.suite_hierarchy_reading import Reader
from exactly_lib.test_suite.processing import SuitesExecutor
from exactly_lib.test_suite.reporters import simple_progress_reporter as sut
from exactly_lib.util import name
from exactly_lib.util.ansi_terminal_color import ForegroundColor
from exactly_lib.util.string import lines_content_with_os_linesep, lines_content
from exactly_lib_test.execution.full_execution.test_resources.result_values import FULL_RESULT_HARD_ERROR, \
    FULL_RESULT_VALIDATE, \
    FULL_RESULT_IMPLEMENTATION_ERROR
from exactly_lib_test.test_resources.files.file_structure import File, empty_file, Dir, DirContents
from exactly_lib_test.test_resources.files.str_std_out_files import StringStdOutFiles
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir_as_cwd
from exactly_lib_test.test_suite.test_resources.environment import default_environment
from exactly_lib_test.test_suite.test_resources.processing_utils import TestCaseProcessorThatGivesConstant, \
    FULL_RESULT_PASS, test_suite, DUMMY_CASE_PROCESSING, test_case, FULL_RESULT_FAIL, FULL_RESULT_SKIP


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestInvalidSuite),
        unittest.makeSuite(TestExecutionOfSuite),
        unittest.makeSuite(TestFinalResultFormatting)
    ])


def _suite_begin(file_name: str) -> str:
    return 'suite ' + file_name + ': begin'


def _suite_end(file_name: str) -> str:
    return 'suite ' + file_name + ': end'


def _case(file_name: str, exit_value: case_ev.ExitValue) -> str:
    return 'case  ' + file_name + ': (__TIME__s) ' + exit_value.exit_identifier


class TestInvalidSuite(unittest.TestCase):
    def test(self):
        # ARRANGE #
        reporter = sut.SimpleProgressRootSuiteProcessingReporter()
        str_std_out_files = StringStdOutFiles()
        exit_value = ExitValue(1, 'IDENTIFIER', ForegroundColor.BLACK)
        # ACT #
        reporter.report_invalid_suite(exit_value,
                                      str_std_out_files.reporting_environment)
        # ASSERT #
        str_std_out_files.finish()
        self.assertEqual(exit_value.exit_identifier + os.linesep,
                         str_std_out_files.stdout_contents,
                         'Output to stdout')
        self.assertEqual('',
                         str_std_out_files.stderr_contents,
                         'Output to stderr')


class TestExecutionOfSuite(unittest.TestCase):
    def test_single_empty_suite(self):
        # ARRANGE #
        expected_exit_value = suite_ev.ALL_PASS
        expected_output = lines_content_with_os_linesep([
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

        self.assertEqual(expected_exit_value.exit_code, exit_code)
        self.assertEqual(expected_output, std_output_files.stdout_contents)

    def test_suite_with_single_case(self):
        cases = [
            (FULL_RESULT_PASS, case_ev.EXECUTION__PASS, suite_ev.ALL_PASS),
            (FULL_RESULT_FAIL, case_ev.EXECUTION__FAIL, suite_ev.FAILED_TESTS),
            (FULL_RESULT_SKIP, case_ev.EXECUTION__SKIPPED, suite_ev.ALL_PASS),
            (FULL_RESULT_HARD_ERROR, case_ev.EXECUTION__HARD_ERROR, suite_ev.FAILED_TESTS),
            (FULL_RESULT_VALIDATE, case_ev.EXECUTION__VALIDATION_ERROR, suite_ev.FAILED_TESTS),
            (FULL_RESULT_IMPLEMENTATION_ERROR, case_ev.EXECUTION__IMPLEMENTATION_ERROR, suite_ev.FAILED_TESTS),
        ]
        for case_result, expected_case_exit_value, expected_suite_exit_value in cases:
            with self.subTest(case_result_status=case_result.status,
                              expected_case_exit_value=expected_case_exit_value,
                              expected_suite_exit_value=expected_suite_exit_value):
                # ARRANGE #
                expected_output = lines_content_with_os_linesep([
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

                self.assertEqual(expected_suite_exit_value.exit_code, exit_code)
                stdout_contents_prepared_for_assertion = _replace_seconds_with_const(std_output_files.stdout_contents)
                self.assertEqual(expected_output,
                                 stdout_contents_prepared_for_assertion)


class TestFinalResultFormatting(unittest.TestCase):
    def test_with_no_errors(self):
        # ARRANGE #
        elapsed_time = datetime.timedelta(seconds=1)
        num_test_cases = 5
        errors = {}
        # ACT #
        actual_lines = sut.format_final_result_for_valid_suite(num_test_cases, elapsed_time,
                                                               Path.cwd().resolve(),
                                                               errors)
        # ASSERT #
        self._assert_at_least_one_line_was_generated(actual_lines)
        self._assert_line_is_number_of_executed_tests_line(actual_lines[0], num_test_cases)
        self.assertListEqual(actual_lines[1:],
                             [],
                             'Lines after "Ran ..."')

    def test_that_report_of_failing_tests_are_grouped_by_exit_identifiers(self):
        cases = [
            (FULL_RESULT_FAIL, case_ev.EXECUTION__FAIL),
            (FULL_RESULT_HARD_ERROR, case_ev.EXECUTION__HARD_ERROR),
            (FULL_RESULT_VALIDATE, case_ev.EXECUTION__VALIDATION_ERROR),
            (FULL_RESULT_IMPLEMENTATION_ERROR, case_ev.EXECUTION__IMPLEMENTATION_ERROR),
        ]
        test_case_file_name = 'test-case-file'
        for case_result, expected_case_exit_value in cases:
            with self.subTest(case_result_status=case_result.status,
                              expected_case_exit_value=expected_case_exit_value):
                # ARRANGE #

                root_suite = test_suite('root file name', [], [test_case(test_case_file_name)])
                test_suites = [root_suite]
                std_output_files = StringStdOutFiles()
                executor = _suite_executor_for_case_processing_that_unconditionally(case_result,
                                                                                    root_suite,
                                                                                    std_output_files,
                                                                                    Path())
                # ACT #

                executor.execute_and_report(test_suites)

                # ASSERT #

                std_output_files.finish()

                stderr_contents = std_output_files.stderr_contents
                exit_ident_pos = stderr_contents.find(expected_case_exit_value.exit_identifier)

                self.assertNotEqual(-1,
                                    exit_ident_pos,
                                    'stderr must contain the exit identifier')
                start_of_exit_ident_group = stderr_contents[exit_ident_pos:]

                group_elements = start_of_exit_ident_group.split()

                self.assertEqual(
                    len(group_elements),
                    2,
                    'Expecting to find EXIT_IDENTIFIER followed by CASE-FILE-NAME as final contents of stderr')

                self.assertEqual(expected_case_exit_value.exit_identifier,
                                 group_elements[0],
                                 'Expects the exit identifier as a single word')

                self.assertEqual(test_case_file_name,
                                 group_elements[1],
                                 'Expects the test case file name to follow the exit identifier')

    def test_with_multiple_errors(self):
        # ARRANGE #
        elapsed_time = datetime.timedelta(seconds=1)
        num_test_cases = 6
        rel_root = Path.cwd().resolve()
        the_exit_identifier = 'identifier_4'
        errors = {
            the_exit_identifier:
                [
                    test_case_reference_of_source_file(rel_root / Path('fip-1') / 'case-1'),
                    test_case_reference_of_source_file(rel_root / Path('fip-2') / 'case-2'),
                ],
            'longer_identifier_12':
                [
                    test_case_reference_of_source_file(rel_root / Path('fip-3') / 'case-3'),
                ],
        }
        # ACT #
        actual_lines = sut.format_final_result_for_valid_suite(num_test_cases, elapsed_time,
                                                               rel_root,
                                                               errors)
        # ASSERT #
        self._assert_at_least_one_line_was_generated(actual_lines)
        self._assert_line_is_number_of_executed_tests_line(actual_lines[0], num_test_cases)
        self.assertEqual(
            ['',
             _NUMBER_OF_ERRORS.of(3),
             ''],
            actual_lines[1:4],
            'Reporting of number of unsuccessful tests (including separating lines)')
        self.assertListEqual([the_exit_identifier,
                              '  ' + str(Path('fip-1') / Path('case-1')),
                              '  ' + str(Path('fip-2') / Path('case-2')),
                              'longer_identifier_12',
                              '  ' + str(Path('fip-3') / Path('case-3')),
                              ],
                             actual_lines[4:],
                             'Lines after "Ran ..."')

    def test_with_error_of_path_below_relativity_root(self):
        # ARRANGE #
        elapsed_time = datetime.timedelta(seconds=1)
        num_test_cases = 6
        rel_root = Path.cwd().resolve()
        the_exit_identifier = 'exit_identifier_4'
        errors = {
            the_exit_identifier:
                [
                    test_case_reference_of_source_file(rel_root.parent / Path('fip-1') / 'case-1'),
                ],
        }
        # ACT #
        actual_lines = sut.format_final_result_for_valid_suite(num_test_cases, elapsed_time,
                                                               rel_root,
                                                               errors)
        # ASSERT #
        self._assert_at_least_one_line_was_generated(actual_lines)
        self._assert_line_is_number_of_executed_tests_line(actual_lines[0], num_test_cases)
        self.assertEqual(
            ['',
             _NUMBER_OF_ERRORS.of(1),
             ''],
            actual_lines[1:4],
            'Reporting of number of unsuccessful tests (including separating lines)')
        self.assertListEqual([the_exit_identifier,
                              '  ' + str(rel_root.parent / Path('fip-1') / Path('case-1')),
                              ],
                             actual_lines[4:],
                             'Lines after "Num unsuccessful ..."')

    def test_with_error_of_path_below_relativity_root__file_names_from_applied_hierarchy_reader(self):
        # ARRANGE #
        elapsed_time = datetime.timedelta(seconds=1)
        num_test_cases = 6
        case_file = empty_file('test.case')
        suite_file = File('test.suite', lines_content([case_file.name]))
        dir_with_suite = Dir('dir-with-suite',
                             [suite_file,
                              case_file])

        with tmp_dir_as_cwd(DirContents([dir_with_suite])) as cwd_abs_path:
            read_suite_hierarchy = Reader(default_environment()).apply(dir_with_suite.name_as_path / suite_file.name)
        self.assertEqual(1,
                         len(read_suite_hierarchy.test_cases),
                         'Sanity check: number of read cases')
        test_case_file_reference = read_suite_hierarchy.test_cases[0]

        the_exit_identifier = 'exit_identifier_4'
        errors = {
            the_exit_identifier: [
                test_case_file_reference,
            ],
        }
        # ACT #
        actual_lines = sut.format_final_result_for_valid_suite(num_test_cases, elapsed_time,
                                                               cwd_abs_path,
                                                               errors)
        # ASSERT #
        self._assert_at_least_one_line_was_generated(actual_lines)
        self._assert_line_is_number_of_executed_tests_line(actual_lines[0], num_test_cases)
        self.assertEqual(
            ['',
             _NUMBER_OF_ERRORS.of(1),
             ''],
            actual_lines[1:4],
            'Reporting of number of unsuccessful tests (including separating lines)')
        self.assertListEqual([the_exit_identifier,
                              '  ' + str(dir_with_suite.name_as_path / case_file.name_as_path),
                              ],
                             actual_lines[4:],
                             'Lines after "Num unsuccessful ..."')

    def _assert_at_least_one_line_was_generated(self, actual_lines):
        if not actual_lines:
            self.fail('No lines at all was generated')

    def _assert_line_is_number_of_executed_tests_line(self, line: str, num_cases: int):
        reg_ex = '^Ran %d tests in .*' % num_cases
        self.assertRegex(line,
                         reg_ex,
                         'Line that reports number of tests and elapsed time')


def _number_of_unsuccessful_tests_line(num_cases: int) -> str:
    return _NUMBER_OF_ERRORS.of(num_cases)


_NUMBER_OF_ERRORS = name.NumberOfItemsString(name.name_with_plural_s('error'))


def _suite_executor_for_case_processing_that_unconditionally(execution_result: FullExeResult,
                                                             root_suite: structure.TestSuiteHierarchy,
                                                             std_output_files: StringStdOutFiles,
                                                             root_file_path: Path) -> SuitesExecutor:
    factory = sut.SimpleProgressRootSuiteProcessingReporter()
    execution_reporter = factory.execution_reporter(root_suite, std_output_files.reporting_environment, root_file_path)
    case_result = test_case_processing.new_executed(execution_result)
    return processing.SuitesExecutor(execution_reporter, DUMMY_CASE_PROCESSING,
                                     lambda conf: TestCaseProcessorThatGivesConstant(case_result))


def _replace_seconds_with_const(string_with_seconds_in_decimal_notation: str) -> str:
    return _TIME_ATTRIBUTE_RE.sub(TIME_VALUE_REPLACEMENT, string_with_seconds_in_decimal_notation)


_TIME_ATTRIBUTE_RE = re.compile(r'[0-9]+(\.[0-9]+)?')
TIME_VALUE_REPLACEMENT = '__TIME__'
