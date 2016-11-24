import pathlib
import unittest
from pathlib import Path

from exactly_lib.execution.result import new_skipped
from exactly_lib.processing import test_case_processing as tcp
from exactly_lib.processing.test_case_processing import TestCaseSetup, new_internal_error, new_executed, \
    new_access_error
from exactly_lib.test_suite import exit_values
from exactly_lib.test_suite import reporting
from exactly_lib.test_suite import structure
from exactly_lib.test_suite.enumeration import DepthFirstEnumerator
from exactly_lib.test_suite.execution import Executor
from exactly_lib.test_suite.instruction_set.parse import SuiteSyntaxError
from exactly_lib.test_suite.suite_hierarchy_reading import SuiteHierarchyReader
from exactly_lib.util import line_source
from exactly_lib_test.test_case.test_resources import error_info
from exactly_lib_test.test_resources.str_std_out_files import StringStdOutFiles
from exactly_lib_test.test_suite.test_resources.execution_utils import \
    TestCaseProcessorThatGivesConstant, DUMMY_CASE_PROCESSING, \
    FULL_RESULT_PASS, test_suite, TestCaseProcessorThatGivesConstantPerCase
from exactly_lib_test.test_suite.test_resources.suite_reporting import ExecutionTracingReporterFactory, \
    ExecutionTracingRootSuiteReporter, EventType, ExecutionTracingSubSuiteProgressReporter


class TestError(unittest.TestCase):
    def test_error_when_reading_suite_structure(self):
        # ARRANGE #
        str_std_out_files = StringStdOutFiles()
        suite_hierarchy_reader = ReaderThatRaisesParseError()
        reporter_factory = ExecutionTracingReporterFactory()
        executor = Executor(DUMMY_CASE_PROCESSING,
                            str_std_out_files.stdout_files,
                            suite_hierarchy_reader,
                            reporter_factory,
                            DepthFirstEnumerator(),
                            lambda x: TestCaseProcessorThatRaisesUnconditionally(),
                            Path('root-suite-file'))
        # ACT #
        exit_code = executor.execute()
        # ASSERT #
        check_exit_code_and_empty_stdout(self,
                                         exit_values.INVALID_SUITE.exit_code,
                                         exit_code,
                                         str_std_out_files)
        ExpectedSuiteReporting.check_list(self, [], reporter_factory.complete_suite_reporter)

    def test_internal_error_in_test_case_processor(self):
        # ARRANGE #
        str_std_out_files = StringStdOutFiles()
        test_case = TestCaseSetup(Path('test-case'))
        root = test_suite('root', [], [test_case])
        suite_hierarchy_reader = ReaderThatGivesConstantSuite(root)
        reporter_factory = ExecutionTracingReporterFactory()
        executor = Executor(DUMMY_CASE_PROCESSING,
                            str_std_out_files.stdout_files,
                            suite_hierarchy_reader,
                            reporter_factory,
                            DepthFirstEnumerator(),
                            lambda config: TestCaseProcessorThatRaisesUnconditionally(),
                            pathlib.Path('root-suite-file'))
        # ACT #
        exit_code = executor.execute()
        # ASSERT #
        check_exit_code_and_empty_stdout(self,
                                         ExecutionTracingRootSuiteReporter.VALID_SUITE_EXIT_CODE,
                                         exit_code,
                                         str_std_out_files)
        ExpectedSuiteReporting.check_list(
            self,
            [ExpectedSuiteReporting(root, [(test_case, tcp.Status.INTERNAL_ERROR)])],
            reporter_factory.complete_suite_reporter)


class TestReturnValueFromTestCaseProcessor(unittest.TestCase):
    def test_internal_error(self):
        result = new_internal_error(error_info.of_message('message'))
        self._helper_for_test_of_return_value_from_test_case_processor(result)

    def test_reading_error(self):
        result = new_access_error(tcp.AccessErrorType.FILE_ACCESS_ERROR,
                                  error_info.of_message('message'))
        self._helper_for_test_of_return_value_from_test_case_processor(result)

    def test_executed__skipped(self):
        result = new_executed(new_skipped())
        self._helper_for_test_of_return_value_from_test_case_processor(result)

    def test_executed__pass(self):
        result = new_executed(FULL_RESULT_PASS)
        self._helper_for_test_of_return_value_from_test_case_processor(result)

    def _helper_for_test_of_return_value_from_test_case_processor(self,
                                                                  result: tcp.Result):
        # ARRANGE #
        str_std_out_files = StringStdOutFiles()
        test_case = TestCaseSetup(Path('test-case'))
        root = test_suite('root', [], [test_case])
        suite_hierarchy_reader = ReaderThatGivesConstantSuite(root)
        reporter_factory = ExecutionTracingReporterFactory()
        executor = Executor(DUMMY_CASE_PROCESSING,
                            str_std_out_files.stdout_files,
                            suite_hierarchy_reader,
                            reporter_factory,
                            DepthFirstEnumerator(),
                            lambda config: TestCaseProcessorThatGivesConstant(result),
                            pathlib.Path('root-suite-file'))
        # ACT #
        exit_code = executor.execute()
        # ASSERT #
        check_exit_code_and_empty_stdout(self,
                                         ExecutionTracingRootSuiteReporter.VALID_SUITE_EXIT_CODE,
                                         exit_code,
                                         str_std_out_files)
        ExpectedSuiteReporting.check_list(
            self,
            [ExpectedSuiteReporting(root, [(test_case, result.status)])],
            reporter_factory.complete_suite_reporter)


class TestComplexSuite(unittest.TestCase):
    def test_single_suite_with_test_cases_with_different_result(self):
        # ARRANGE #
        reporter_factory = ExecutionTracingReporterFactory()
        str_std_out_files = StringStdOutFiles()
        tc_internal_error = TestCaseSetup(Path('internal error'))
        tc_access_error = TestCaseSetup(Path('access error'))
        tc_executed = TestCaseSetup(Path('executed'))
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
        executor = Executor(DUMMY_CASE_PROCESSING,
                            str_std_out_files.stdout_files,
                            suite_hierarchy_reader,
                            reporter_factory,
                            DepthFirstEnumerator(),
                            lambda config: test_case_processor,
                            pathlib.Path('root-suite-file'))
        # ACT #
        exit_code = executor.execute()
        # ASSERT #
        check_exit_code_and_empty_stdout(self,
                                         ExecutionTracingRootSuiteReporter.VALID_SUITE_EXIT_CODE,
                                         exit_code,
                                         str_std_out_files)
        ExpectedSuiteReporting.check_list(
            self,
            expected_suites,
            reporter_factory.complete_suite_reporter)

    def test_suite_execution_order_using_empty_suites(self):
        # ARRANGE #
        reporter_factory = ExecutionTracingReporterFactory()
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
        executor = Executor(DUMMY_CASE_PROCESSING,
                            str_std_out_files.stdout_files,
                            suite_hierarchy_reader,
                            reporter_factory,
                            DepthFirstEnumerator(),
                            lambda config: TestCaseProcessorThatGivesConstantPerCase({}),
                            pathlib.Path('root-suite-file'))
        # ACT #
        exit_code = executor.execute()
        # ASSERT #
        check_exit_code_and_empty_stdout(self,
                                         ExecutionTracingRootSuiteReporter.VALID_SUITE_EXIT_CODE,
                                         exit_code,
                                         str_std_out_files)
        ExpectedSuiteReporting.check_list(
            self,
            expected_suites,
            reporter_factory.complete_suite_reporter)

    def test_complex_suite_structure_with_test_cases(self):
        # ARRANGE #
        reporter_factory = ExecutionTracingReporterFactory()
        str_std_out_files = StringStdOutFiles()
        tc_internal_error_11 = TestCaseSetup(Path('internal error 11'))
        tc_internal_error_21 = TestCaseSetup(Path('internal error 21'))
        tc_access_error_1 = TestCaseSetup(Path('access error A'))
        tc_access_error_12 = TestCaseSetup(Path('access error 12'))
        tc_executed_11 = TestCaseSetup(Path('executed 11'))
        tc_executed_12 = TestCaseSetup(Path('executed 12'))
        tc_executed_1 = TestCaseSetup(Path('executed 1'))
        tc_executed_2 = TestCaseSetup(Path('executed 2'))
        tc_executed_root = TestCaseSetup(Path('executed root'))
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
        executor = Executor(DUMMY_CASE_PROCESSING,
                            str_std_out_files.stdout_files,
                            suite_hierarchy_reader,
                            reporter_factory,
                            DepthFirstEnumerator(),
                            lambda config: test_case_processor,
                            pathlib.Path('root-suite-file'))
        # ACT #
        exit_code = executor.execute()
        # ASSERT #
        check_exit_code_and_empty_stdout(self,
                                         ExecutionTracingRootSuiteReporter.VALID_SUITE_EXIT_CODE,
                                         exit_code,
                                         str_std_out_files)
        ExpectedSuiteReporting.check_list(
            self,
            expected_suites,
            reporter_factory.complete_suite_reporter)


def check_exit_code_and_empty_stdout(put: unittest.TestCase,
                                     expected_exit_code: int,
                                     actual_exit_code: int,
                                     str_std_out_files: StringStdOutFiles):
    put.assertEqual(expected_exit_code,
                    actual_exit_code,
                    'Exit code')
    put.assertEqual('',
                    str_std_out_files.stdout_contents,
                    'Output to stdout')


class TestCaseProcessorThatRaisesUnconditionally(tcp.Processor):
    def apply(self, test_case: TestCaseSetup) -> tcp.Result:
        raise NotImplementedError('Unconditional expected exception from test implementation')


class ReaderThatRaisesParseError(SuiteHierarchyReader):
    def apply(self, suite_file_path: pathlib.Path) -> structure.TestSuite:
        raise SuiteSyntaxError(suite_file_path,
                               line_source.Line(1, 'line'),
                               'message')


class ReaderThatGivesConstantSuite(SuiteHierarchyReader):
    def __init__(self,
                 constant: structure.TestSuite):
        self.constant = constant

    def apply(self, suite_file_path: pathlib.Path) -> structure.TestSuite:
        return self.constant


class ExpectedSuiteReporting(tuple):
    def __new__(cls,
                test_suite: structure.TestSuite,
                case_and_result_status_list: list):
        """
        :param case_and_result_status_list: [(TestCase, tcp.Status)]
        """
        return tuple.__new__(cls, (test_suite, case_and_result_status_list))

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
    def suite(self) -> structure.TestSuite:
        return self[0]

    @property
    def case_and_result_status_list(self) -> list:
        return self[1]

    def check(self,
              put: unittest.TestCase,
              sr: reporting.SubSuiteReporter,
              msg_header=''):
        listener = sr.listener()
        assert isinstance(listener, ExecutionTracingSubSuiteProgressReporter)
        put.assertIs(self.suite,
                     listener.sub_suite,
                     msg_header + 'Suite instance')
        put.assertEqual(len(self.case_and_result_status_list),
                        len(listener.case_begin_list),
                        msg_header + 'Number of invocations of case-begin')
        self._assert_correct_progress_reporter_invocations(listener, msg_header, put)
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
                         msg_header + 'Registered %s instance for case-begin' % str(TestCaseSetup))
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
    def _assert_case_is_registered_correctly(expected_case: TestCaseSetup,
                                             expected_status: tcp.Status,
                                             actual_begin_case,
                                             actual_end_case,
                                             actual_end_proc_result,
                                             msg_header,
                                             put):
        put.assertIs(expected_case,
                     actual_begin_case,
                     msg_header + 'Registered %s instance for case-begin' % str(TestCaseSetup))
        put.assertIs(expected_case,
                     actual_end_case,
                     msg_header + 'Registered %s instance for case-end' % str(TestCaseSetup))
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


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestError))
    ret_val.addTest(unittest.makeSuite(TestReturnValueFromTestCaseProcessor))
    ret_val.addTest(unittest.makeSuite(TestComplexSuite))
    return ret_val


def run_suite():
    unittest.TextTestRunner().run(suite())


if __name__ == '__main__':
    run_suite()
