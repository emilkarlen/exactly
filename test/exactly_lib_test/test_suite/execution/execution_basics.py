import pathlib
import unittest
from pathlib import Path
from typing import List, Tuple

from exactly_lib.execution.full_execution.result import new_skipped
from exactly_lib.processing import test_case_processing as tcp
from exactly_lib.processing.test_case_processing import TestCaseFileReference, new_internal_error, new_executed, \
    new_access_error, test_case_reference_of_source_file
from exactly_lib.test_suite import exit_values
from exactly_lib.test_suite import reporting
from exactly_lib.test_suite.enumeration import DepthFirstEnumerator
from exactly_lib.test_suite.file_reading.exception import SuiteSyntaxError
from exactly_lib.test_suite.file_reading.suite_hierarchy_reading import SuiteHierarchyReader
from exactly_lib.test_suite.processing import Processor
from exactly_lib.test_suite.structure import TestSuiteHierarchy
from exactly_lib.util import line_source
from exactly_lib_test.test_case.test_resources import error_info
from exactly_lib_test.test_resources.files.str_std_out_files import StringStdOutFiles
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_suite.test_resources.execution_utils import \
    TestCaseProcessorThatGivesConstant, DUMMY_CASE_PROCESSING, \
    FULL_RESULT_PASS, test_suite, TestCaseProcessorThatGivesConstantPerCase
from exactly_lib_test.test_suite.test_resources.suite_reporting import ExecutionTracingProcessingReporter, \
    ExecutionTracingRootSuiteReporter, EventType, ExecutionTracingSubSuiteProgressReporter


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestError))
    ret_val.addTest(unittest.makeSuite(TestReturnValueFromTestCaseProcessor))
    ret_val.addTest(unittest.makeSuite(TestComplexSuite))
    return ret_val


class TestError(unittest.TestCase):
    def test_error_when_reading_suite_structure(self):
        # ARRANGE #
        str_std_out_files = StringStdOutFiles()
        suite_hierarchy_reader = ReaderThatRaisesParseError()
        reporter = ExecutionTracingProcessingReporter()
        executor = Processor(DUMMY_CASE_PROCESSING,
                             suite_hierarchy_reader,
                             reporter,
                             DepthFirstEnumerator(),
                             lambda x: TestCaseProcessorThatRaisesUnconditionally())
        # ACT #
        exit_code = executor.process(Path('root-suite-file'), str_std_out_files.stdout_files)
        # ASSERT #
        check_exit_code_and_empty_stdout(self,
                                         exit_values.INVALID_SUITE.exit_code,
                                         exit_code,
                                         str_std_out_files)
        expected_invalid_suite_invocations = asrt.matches_sequence([
            asrt.equals(exit_values.INVALID_SUITE),
        ])
        expected_invalid_suite_invocations.apply_with_message(self,
                                                              reporter.report_invalid_suite_invocations,
                                                              'report_invalid_suite_invocations')
        ExpectedSuiteReporting.check_list(self, [], reporter.complete_suite_reporter)

    def test_internal_error_in_test_case_processor(self):
        # ARRANGE #
        str_std_out_files = StringStdOutFiles()
        test_case = test_case_reference_of_source_file(Path('test-case'))
        root = test_suite('root', [], [test_case])
        suite_hierarchy_reader = ReaderThatGivesConstantSuite(root)
        reporter = ExecutionTracingProcessingReporter()
        executor = Processor(DUMMY_CASE_PROCESSING,
                             suite_hierarchy_reader,
                             reporter,
                             DepthFirstEnumerator(),
                             lambda config: TestCaseProcessorThatRaisesUnconditionally())
        # ACT #
        exit_code = executor.process(pathlib.Path('root-suite-file'), str_std_out_files.stdout_files)
        # ASSERT #
        check_exit_code_and_empty_stdout(self,
                                         ExecutionTracingRootSuiteReporter.VALID_SUITE_EXIT_CODE,
                                         exit_code,
                                         str_std_out_files)
        ExpectedSuiteReporting.check_list(
            self,
            [ExpectedSuiteReporting(root, [(test_case, tcp.Status.INTERNAL_ERROR)])],
            reporter.complete_suite_reporter)


class TestReturnValueFromTestCaseProcessor(unittest.TestCase):
    def test_internal_error(self):
        result = new_internal_error(error_info.of_message('message'))
        self._check(result)

    def test_reading_error(self):
        result = new_access_error(tcp.AccessErrorType.FILE_ACCESS_ERROR,
                                  error_info.of_message('message'))
        self._check(result)

    def test_executed__skipped(self):
        result = new_executed(new_skipped())
        self._check(result)

    def test_executed__pass(self):
        result = new_executed(FULL_RESULT_PASS)
        self._check(result)

    def _check(self,
               result: tcp.Result):
        # ARRANGE #
        str_std_out_files = StringStdOutFiles()
        test_case = test_case_reference_of_source_file(Path('test-case'))
        root = test_suite('root', [], [test_case])
        suite_hierarchy_reader = ReaderThatGivesConstantSuite(root)
        reporter = ExecutionTracingProcessingReporter()
        executor = Processor(DUMMY_CASE_PROCESSING,
                             suite_hierarchy_reader,
                             reporter,
                             DepthFirstEnumerator(),
                             lambda config: TestCaseProcessorThatGivesConstant(result))
        # ACT #
        exit_code = executor.process(pathlib.Path('root-suite-file'), str_std_out_files.stdout_files)
        # ASSERT #
        check_exit_code_and_empty_stdout(self,
                                         ExecutionTracingRootSuiteReporter.VALID_SUITE_EXIT_CODE,
                                         exit_code,
                                         str_std_out_files)
        ExpectedSuiteReporting.check_list(
            self,
            [ExpectedSuiteReporting(root, [(test_case, result.status)])],
            reporter.complete_suite_reporter)


class TestComplexSuite(unittest.TestCase):
    def test_single_suite_with_test_cases_with_different_result(self):
        # ARRANGE #
        reporter = ExecutionTracingProcessingReporter()
        str_std_out_files = StringStdOutFiles()
        tc_internal_error = test_case_reference_of_source_file(Path('internal error'))
        tc_access_error = test_case_reference_of_source_file(Path('access error'))
        tc_executed = test_case_reference_of_source_file(Path('executed'))
        root = test_suite(
            'root',
            [],
            [
                tc_internal_error,
                tc_access_error,
                tc_executed,
            ])
        test_case_processor = TestCaseProcessorThatGivesConstantPerCase({
            id(tc_internal_error): new_internal_error(error_info.of_message('message')),
            id(tc_access_error): new_access_error(
                tcp.AccessErrorType.SYNTAX_ERROR, error_info.of_message('syntax error')),
            id(tc_executed): new_executed(FULL_RESULT_PASS),
        })
        expected_suites = [
            ExpectedSuiteReporting(root,
                                   [
                                       (tc_internal_error, tcp.Status.INTERNAL_ERROR),
                                       (tc_access_error, tcp.Status.ACCESS_ERROR),
                                       (tc_executed, tcp.Status.EXECUTED),
                                   ])
        ]
        suite_hierarchy_reader = ReaderThatGivesConstantSuite(root)
        executor = Processor(DUMMY_CASE_PROCESSING,
                             suite_hierarchy_reader,
                             reporter,
                             DepthFirstEnumerator(),
                             lambda config: test_case_processor)
        # ACT #
        exit_code = executor.process(pathlib.Path('root-suite-file'), str_std_out_files.stdout_files)
        # ASSERT #
        check_exit_code_and_empty_stdout(self,
                                         ExecutionTracingRootSuiteReporter.VALID_SUITE_EXIT_CODE,
                                         exit_code,
                                         str_std_out_files)
        ExpectedSuiteReporting.check_list(
            self,
            expected_suites,
            reporter.complete_suite_reporter)

    def test_suite_execution_order_using_empty_suites(self):
        # ARRANGE #
        reporter = ExecutionTracingProcessingReporter()
        str_std_out_files = StringStdOutFiles()
        sub11 = test_suite('11', [], [])
        sub12 = test_suite('12', [], [])
        sub1 = test_suite('1', [sub11, sub12], [])
        sub21 = test_suite('21', [], [])
        sub2 = test_suite('2', [sub21], [])
        root = test_suite('root', [sub1, sub2], [])

        expected_suites = [
            ExpectedSuiteReporting(sub11, []),
            ExpectedSuiteReporting(sub12, []),
            ExpectedSuiteReporting(sub1, []),
            ExpectedSuiteReporting(sub21, []),
            ExpectedSuiteReporting(sub2, []),
            ExpectedSuiteReporting(root, []),
        ]
        suite_hierarchy_reader = ReaderThatGivesConstantSuite(root)
        executor = Processor(DUMMY_CASE_PROCESSING,
                             suite_hierarchy_reader,
                             reporter,
                             DepthFirstEnumerator(),
                             lambda config: TestCaseProcessorThatGivesConstantPerCase({}))
        # ACT #
        exit_code = executor.process(pathlib.Path('root-suite-file'), str_std_out_files.stdout_files)
        # ASSERT #
        check_exit_code_and_empty_stdout(self,
                                         ExecutionTracingRootSuiteReporter.VALID_SUITE_EXIT_CODE,
                                         exit_code,
                                         str_std_out_files)
        ExpectedSuiteReporting.check_list(
            self,
            expected_suites,
            reporter.complete_suite_reporter)

    def test_complex_suite_structure_with_test_cases(self):
        # ARRANGE #
        reporter = ExecutionTracingProcessingReporter()
        str_std_out_files = StringStdOutFiles()
        tc_internal_error_11 = test_case_reference_of_source_file(Path('internal error 11'))
        tc_internal_error_21 = test_case_reference_of_source_file(Path('internal error 21'))
        tc_access_error_1 = test_case_reference_of_source_file(Path('access error A'))
        tc_access_error_12 = test_case_reference_of_source_file(Path('access error 12'))
        tc_executed_11 = test_case_reference_of_source_file(Path('executed 11'))
        tc_executed_12 = test_case_reference_of_source_file(Path('executed 12'))
        tc_executed_1 = test_case_reference_of_source_file(Path('executed 1'))
        tc_executed_2 = test_case_reference_of_source_file(Path('executed 2'))
        tc_executed_root = test_case_reference_of_source_file(Path('executed root'))
        test_case_processor = TestCaseProcessorThatGivesConstantPerCase({
            id(tc_internal_error_11): new_internal_error(error_info.of_message('message A')),
            id(tc_internal_error_21): new_internal_error(error_info.of_message('message B')),
            id(tc_access_error_1): new_access_error(
                tcp.AccessErrorType.SYNTAX_ERROR, error_info.of_message('syntax error')),
            id(tc_access_error_12): new_access_error(tcp.AccessErrorType.FILE_ACCESS_ERROR,
                                                     error_info.of_message('file access error')),
            id(tc_executed_11): new_executed(FULL_RESULT_PASS),
            id(tc_executed_12): new_executed(FULL_RESULT_PASS),
            id(tc_executed_1): new_executed(FULL_RESULT_PASS),
            id(tc_executed_2): new_executed(FULL_RESULT_PASS),
            id(tc_executed_root): new_executed(FULL_RESULT_PASS),
        })
        sub11 = test_suite('11', [], [tc_internal_error_11,
                                      tc_executed_11])
        sub12 = test_suite('12', [], [tc_executed_12,
                                      tc_access_error_12])
        sub1 = test_suite('1', [sub11, sub12], [tc_access_error_1,
                                                tc_executed_1])
        sub21 = test_suite('21', [], [tc_internal_error_21])
        sub2 = test_suite('2', [sub21], [tc_executed_2])
        sub3 = test_suite('2', [], [])
        root = test_suite('root', [sub1, sub2, sub3], [tc_executed_root])

        expected_suites = [
            ExpectedSuiteReporting(sub11, [(tc_internal_error_11, tcp.Status.INTERNAL_ERROR),
                                           (tc_executed_11, tcp.Status.EXECUTED)]),
            ExpectedSuiteReporting(sub12, [(tc_executed_12, tcp.Status.EXECUTED),
                                           (tc_access_error_12, tcp.Status.ACCESS_ERROR)]),
            ExpectedSuiteReporting(sub1, [(tc_access_error_1, tcp.Status.ACCESS_ERROR),
                                          (tc_executed_1, tcp.Status.EXECUTED)]),
            ExpectedSuiteReporting(sub21, [(tc_internal_error_21, tcp.Status.INTERNAL_ERROR)]),
            ExpectedSuiteReporting(sub2, [(tc_executed_2, tcp.Status.EXECUTED)]),
            ExpectedSuiteReporting(sub3, []),
            ExpectedSuiteReporting(root, [(tc_executed_root, tcp.Status.EXECUTED)]),
        ]
        suite_hierarchy_reader = ReaderThatGivesConstantSuite(root)
        executor = Processor(DUMMY_CASE_PROCESSING,
                             suite_hierarchy_reader,
                             reporter,
                             DepthFirstEnumerator(),
                             lambda config: test_case_processor)
        # ACT #
        exit_code = executor.process(pathlib.Path('root-suite-file'), str_std_out_files.stdout_files)
        # ASSERT #
        check_exit_code_and_empty_stdout(self,
                                         ExecutionTracingRootSuiteReporter.VALID_SUITE_EXIT_CODE,
                                         exit_code,
                                         str_std_out_files)
        ExpectedSuiteReporting.check_list(
            self,
            expected_suites,
            reporter.complete_suite_reporter)


def check_exit_code_and_empty_stdout(put: unittest.TestCase,
                                     expected_exit_code: int,
                                     actual_exit_code: int,
                                     str_std_out_files: StringStdOutFiles):
    str_std_out_files.finish()
    put.assertEqual(expected_exit_code,
                    actual_exit_code,
                    'Exit code')
    put.assertEqual('',
                    str_std_out_files.stdout_contents,
                    'Output to stdout')


class TestCaseProcessorThatRaisesUnconditionally(tcp.Processor):
    def apply(self, test_case: TestCaseFileReference) -> tcp.Result:
        raise NotImplementedError('Unconditional expected exception from test implementation')


class ReaderThatRaisesParseError(SuiteHierarchyReader):
    def apply(self, suite_file_path: pathlib.Path) -> TestSuiteHierarchy:
        raise SuiteSyntaxError(suite_file_path,
                               line_source.single_line_sequence(1, 'line'),
                               'message')


class ReaderThatGivesConstantSuite(SuiteHierarchyReader):
    def __init__(self,
                 constant: TestSuiteHierarchy):
        self.constant = constant

    def apply(self, suite_file_path: pathlib.Path) -> TestSuiteHierarchy:
        return self.constant


class ExpectedSuiteReporting(tuple):
    def __new__(cls,
                suite_hierarchy: TestSuiteHierarchy,
                case_and_result_status_list: List[Tuple[TestCaseFileReference, tcp.Status]]):
        return tuple.__new__(cls, (suite_hierarchy, case_and_result_status_list))

    @staticmethod
    def check_list(put: unittest.TestCase,
                   expected: list,
                   actual: ExecutionTracingRootSuiteReporter):
        """
        :param expected: [ExpectedSuiteReporting]
        """
        for i, (e, a) in enumerate(zip(expected, actual.sub_suite_reporters)):
            e.check(put, a, 'Suite at index ' + str(i) + ': ')
        put.assertEqual(len(expected),
                        len(actual.sub_suite_reporters),
                        'Number of suites')

    @property
    def suite(self) -> TestSuiteHierarchy:
        return self[0]

    @property
    def case_and_result_status_list(self) -> List[Tuple[TestCaseFileReference, tcp.Status]]:
        return self[1]

    def check(self,
              put: unittest.TestCase,
              sr: reporting.SubSuiteReporter,
              msg_header=''):
        progress_reporter = sr.progress_reporter
        assert isinstance(progress_reporter, ExecutionTracingSubSuiteProgressReporter)
        put.assertIs(self.suite,
                     progress_reporter.sub_suite,
                     msg_header + 'Suite instance')
        put.assertEqual(len(self.case_and_result_status_list),
                        len(progress_reporter.case_begin_list),
                        msg_header + 'Number of invocations of case-begin')
        self._assert_correct_progress_reporter_invocations(progress_reporter, msg_header, put)
        self._assert_correct_sub_suite_reporter_invocations(sr, msg_header, put)

    def _assert_correct_sub_suite_reporter_invocations(self,
                                                       sr: reporting.SubSuiteReporter,
                                                       msg_header, put):
        put.assertEqual(len(self.case_and_result_status_list),
                        len(sr.result()),
                        msg_header + 'Number of registered results in ' + str(reporting.SubSuiteReporter))
        for (expected_case, expected_status), (test_case_setup, processing_info) in zip(
                self.case_and_result_status_list,
                sr.result()):
            result = processing_info.result
            put.assertIs(expected_case,
                         test_case_setup,
                         msg_header + 'Registered %s instance for case-begin' % str(TestCaseFileReference))
            put.assertIs(expected_status,
                         result.status,
                         msg_header + 'Registered %s instance for case-end' % str(tcp.Status))

    def _assert_correct_progress_reporter_invocations(self, listener, msg_header, put):
        put.assertEqual(len(self.case_and_result_status_list),
                        len(listener.case_end_list),
                        msg_header + 'Number of invocations of case-end')
        for (exp_case, exp_status), begin_case, (end_case, end_proc_result) in zip(self.case_and_result_status_list,
                                                                                   listener.case_begin_list,
                                                                                   listener.case_end_list):
            self._assert_case_is_registered_correctly(exp_case,
                                                      exp_status,
                                                      begin_case,
                                                      end_case,
                                                      end_proc_result,
                                                      msg_header, put)
        self._check_invokation_sequence(put, listener, msg_header)

    @staticmethod
    def _assert_case_is_registered_correctly(expected_case: TestCaseFileReference,
                                             expected_status: tcp.Status,
                                             actual_begin_case,
                                             actual_end_case,
                                             actual_end_proc_result,
                                             msg_header,
                                             put):
        put.assertIs(expected_case,
                     actual_begin_case,
                     msg_header + 'Registered %s instance for case-begin' % str(TestCaseFileReference))
        put.assertIs(expected_case,
                     actual_end_case,
                     msg_header + 'Registered %s instance for case-end' % str(TestCaseFileReference))
        put.assertIs(expected_status,
                     actual_end_proc_result.status,
                     msg_header + 'Registered %s instance for case-end' % str(tcp.Status))

    def _check_invokation_sequence(self,
                                   put: unittest.TestCase,
                                   sr: ExecutionTracingSubSuiteProgressReporter,
                                   msg_header=''):
        expected_num_cases = len(self.case_and_result_status_list)
        actual_num_events = len(sr.event_type_list)
        expected_num_events = 2 + 2 * expected_num_cases
        put.assertEqual(expected_num_events,
                        actual_num_events,
                        msg_header + 'Total number of events')
        put.assertIs(EventType.SUITE_BEGIN,
                     sr.event_type_list[0],
                     msg_header + 'First event should be ' + str(EventType.SUITE_BEGIN))
        put.assertIs(EventType.SUITE_END,
                     sr.event_type_list[-1],
                     msg_header + 'Last event should be ' + str(EventType.SUITE_END))
        for case_idx in range(1, 1 + 2 * expected_num_cases, 2):
            put.assertIs(EventType.CASE_BEGIN,
                         sr.event_type_list[case_idx],
                         msg_header + 'First event of case processing')
            put.assertIs(EventType.CASE_END,
                         sr.event_type_list[case_idx + 1],
                         msg_header + 'Second event of case processing')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
