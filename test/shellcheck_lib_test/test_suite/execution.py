import enum
import pathlib
from pathlib import Path
import unittest

from shellcheck_lib.test_suite.execution import Executor
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.execution.result import new_skipped, new_pass
from shellcheck_lib.general import line_source
from shellcheck_lib.general import output
from shellcheck_lib.test_case.test_case_struct import TestCase
from shellcheck_lib.test_suite import structure
from shellcheck_lib.test_suite.enumeration import DepthFirstEnumerator
from shellcheck_lib.test_suite.parse import SuiteSyntaxError
from shellcheck_lib.test_suite import reporting
from shellcheck_lib.test_suite import test_case_processing
from shellcheck_lib.test_suite.suite_hierarchy_reading import SuiteHierarchyReader
from shellcheck_lib.test_suite.test_case_processing import TestCaseProcessingStatus, TestCaseProcessingResult, \
    TestCaseAccessError
from shellcheck_lib_test.util.str_std_out_files import StringStdOutFiles


class TestError(unittest.TestCase):
    def test_error_when_reading_suite_structure(self):
        # ARRANGE #
        str_std_out_files = StringStdOutFiles()
        suite_hierarchy_reader = ReaderThatRaisesParseError()
        reporter_factory = ExecutionTracingReporterFactory()
        executor = Executor(str_std_out_files.stdout_files,
                            suite_hierarchy_reader,
                            reporter_factory,
                            DepthFirstEnumerator(),
                            TestCaseProcessorThatRaisesUnconditionally(),
                            Path('root-suite-file'))
        # ACT #
        exit_code = executor.execute()
        # ASSERT #
        check_exit_code_and_empty_stdout(self,
                                         ExecutionTracingCompleteSuiteReporter.INVALID_SUITE_EXIT_CODE,
                                         exit_code,
                                         str_std_out_files)
        ExpectedSuiteReporting.check_list(self, [], reporter_factory.complete_suite_reporter)

    def test_internal_error_in_test_case_processor(self):
        # ARRANGE #
        str_std_out_files = StringStdOutFiles()
        test_case = structure.TestCase(Path('test-case'))
        root = structure.TestSuite(Path('root'), [], [], [test_case])
        suite_hierarchy_reader = ReaderThatGivesConstantSuite(root)
        reporter_factory = ExecutionTracingReporterFactory()
        executor = Executor(str_std_out_files.stdout_files,
                            suite_hierarchy_reader,
                            reporter_factory,
                            DepthFirstEnumerator(),
                            TestCaseProcessorThatRaisesUnconditionally(),
                            pathlib.Path('root-suite-file'))
        # ACT #
        exit_code = executor.execute()
        # ASSERT #
        check_exit_code_and_empty_stdout(self,
                                         ExecutionTracingCompleteSuiteReporter.VALID_SUITE_EXIT_CODE,
                                         exit_code,
                                         str_std_out_files)
        ExpectedSuiteReporting.check_list(
            self,
            [ExpectedSuiteReporting(root, [(test_case, TestCaseProcessingStatus.INTERNAL_ERROR)])],
            reporter_factory.complete_suite_reporter)


class TestReturnValueFromTestCaseProcessor(unittest.TestCase):
    def test_internal_error(self):
        result = test_case_processing.new_internal_error('message')
        self._helper_for_test_of_return_value_from_test_case_processor(result)

    def test_reading_error(self):
        result = test_case_processing.new_access_error(TestCaseAccessError.FILE_ACCESS_ERROR)
        self._helper_for_test_of_return_value_from_test_case_processor(result)

    def test_executed__skipped(self):
        result = test_case_processing.new_executed(new_skipped())
        self._helper_for_test_of_return_value_from_test_case_processor(result)

    def test_executed__pass(self):
        result = test_case_processing.new_executed(FULL_RESULT_PASS)
        self._helper_for_test_of_return_value_from_test_case_processor(result)

    def _helper_for_test_of_return_value_from_test_case_processor(self,
                                                                  result: TestCaseProcessingResult):
        # ARRANGE #
        str_std_out_files = StringStdOutFiles()
        test_case = structure.TestCase(Path('test-case'))
        root = structure.TestSuite(Path('root'), [], [], [test_case])
        suite_hierarchy_reader = ReaderThatGivesConstantSuite(root)
        reporter_factory = ExecutionTracingReporterFactory()
        executor = Executor(str_std_out_files.stdout_files,
                            suite_hierarchy_reader,
                            reporter_factory,
                            DepthFirstEnumerator(),
                            TestCaseProcessorThatGivesConstant(result),
                            pathlib.Path('root-suite-file'))
        # ACT #
        exit_code = executor.execute()
        # ASSERT #
        check_exit_code_and_empty_stdout(self,
                                         ExecutionTracingCompleteSuiteReporter.VALID_SUITE_EXIT_CODE,
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
        tc_internal_error = structure.TestCase(Path('internal error'))
        tc_access_error = structure.TestCase(Path('access error'))
        tc_executed = structure.TestCase(Path('executed'))
        root = structure.TestSuite(
            pathlib.Path('root'),
            [],
            [],
            [
                tc_internal_error,
                tc_access_error,
                tc_executed,
            ])
        test_case_processor = TestCaseProcessorThatGivesConstantPerCase({
            id(tc_internal_error): test_case_processing.new_internal_error('message'),
            id(tc_access_error): test_case_processing.new_access_error(TestCaseAccessError.PARSE_ERROR),
            id(tc_executed): test_case_processing.new_executed(FULL_RESULT_PASS),
        })
        expected_suites = [
            ExpectedSuiteReporting(root,
                                   [
                                       (tc_internal_error, TestCaseProcessingStatus.INTERNAL_ERROR),
                                       (tc_access_error, TestCaseProcessingStatus.ACCESS_ERROR),
                                       (tc_executed, TestCaseProcessingStatus.EXECUTED),
                                   ])
        ]
        suite_hierarchy_reader = ReaderThatGivesConstantSuite(root)
        executor = Executor(str_std_out_files.stdout_files,
                            suite_hierarchy_reader,
                            reporter_factory,
                            DepthFirstEnumerator(),
                            test_case_processor,
                            pathlib.Path('root-suite-file'))
        # ACT #
        exit_code = executor.execute()
        # ASSERT #
        check_exit_code_and_empty_stdout(self,
                                         ExecutionTracingCompleteSuiteReporter.VALID_SUITE_EXIT_CODE,
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
        sub11 = structure.TestSuite(pathlib.Path('11'), [], [], [])
        sub12 = structure.TestSuite(pathlib.Path('12'), [], [], [])
        sub1 = structure.TestSuite(pathlib.Path('1'), [], [sub11, sub12], [])
        sub21 = structure.TestSuite(pathlib.Path('21'), [], [], [])
        sub2 = structure.TestSuite(pathlib.Path('2'), [], [sub21], [])
        root = structure.TestSuite(pathlib.Path('root'), [], [sub1, sub2], [])

        expected_suites = [
            ExpectedSuiteReporting(sub11, []),
            ExpectedSuiteReporting(sub12, []),
            ExpectedSuiteReporting(sub1, []),
            ExpectedSuiteReporting(sub21, []),
            ExpectedSuiteReporting(sub2, []),
            ExpectedSuiteReporting(root, []),
        ]
        suite_hierarchy_reader = ReaderThatGivesConstantSuite(root)
        executor = Executor(str_std_out_files.stdout_files,
                            suite_hierarchy_reader,
                            reporter_factory,
                            DepthFirstEnumerator(),
                            TestCaseProcessorThatGivesConstantPerCase({}),
                            pathlib.Path('root-suite-file'))
        # ACT #
        exit_code = executor.execute()
        # ASSERT #
        check_exit_code_and_empty_stdout(self,
                                         ExecutionTracingCompleteSuiteReporter.VALID_SUITE_EXIT_CODE,
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
        tc_internal_error_11 = structure.TestCase(Path('internal error 11'))
        tc_internal_error_21 = structure.TestCase(Path('internal error 21'))
        tc_access_error_1 = structure.TestCase(Path('access error A'))
        tc_access_error_12 = structure.TestCase(Path('access error 12'))
        tc_executed_11 = structure.TestCase(Path('executed 11'))
        tc_executed_12 = structure.TestCase(Path('executed 12'))
        tc_executed_1 = structure.TestCase(Path('executed 1'))
        tc_executed_2 = structure.TestCase(Path('executed 2'))
        tc_executed_root = structure.TestCase(Path('executed root'))
        test_case_processor = TestCaseProcessorThatGivesConstantPerCase({
            id(tc_internal_error_11): test_case_processing.new_internal_error('message A'),
            id(tc_internal_error_21): test_case_processing.new_internal_error('messageB'),
            id(tc_access_error_1): test_case_processing.new_access_error(TestCaseAccessError.PARSE_ERROR),
            id(tc_access_error_12): test_case_processing.new_access_error(TestCaseAccessError.FILE_ACCESS_ERROR),
            id(tc_executed_11): test_case_processing.new_executed(FULL_RESULT_PASS),
            id(tc_executed_12): test_case_processing.new_executed(FULL_RESULT_PASS),
            id(tc_executed_1): test_case_processing.new_executed(FULL_RESULT_PASS),
            id(tc_executed_2): test_case_processing.new_executed(FULL_RESULT_PASS),
            id(tc_executed_root): test_case_processing.new_executed(FULL_RESULT_PASS),
        })
        sub11 = structure.TestSuite(pathlib.Path('11'), [], [], [tc_internal_error_11,
                                                                 tc_executed_11])
        sub12 = structure.TestSuite(pathlib.Path('12'), [], [], [tc_executed_12,
                                                                 tc_access_error_12])
        sub1 = structure.TestSuite(pathlib.Path('1'), [], [sub11, sub12], [tc_access_error_1,
                                                                           tc_executed_1])
        sub21 = structure.TestSuite(pathlib.Path('21'), [], [], [tc_internal_error_21])
        sub2 = structure.TestSuite(pathlib.Path('2'), [], [sub21], [tc_executed_2])
        sub3 = structure.TestSuite(pathlib.Path('2'), [], [], [])
        root = structure.TestSuite(pathlib.Path('root'), [], [sub1, sub2, sub3], [tc_executed_root])

        expected_suites = [
            ExpectedSuiteReporting(sub11, [(tc_internal_error_11, TestCaseProcessingStatus.INTERNAL_ERROR),
                                           (tc_executed_11, TestCaseProcessingStatus.EXECUTED)]),
            ExpectedSuiteReporting(sub12, [(tc_executed_12, TestCaseProcessingStatus.EXECUTED),
                                           (tc_access_error_12, TestCaseProcessingStatus.ACCESS_ERROR)]),
            ExpectedSuiteReporting(sub1, [(tc_access_error_1, TestCaseProcessingStatus.ACCESS_ERROR),
                                          (tc_executed_1, TestCaseProcessingStatus.EXECUTED)]),
            ExpectedSuiteReporting(sub21, [(tc_internal_error_21, TestCaseProcessingStatus.INTERNAL_ERROR)]),
            ExpectedSuiteReporting(sub2, [(tc_executed_2, TestCaseProcessingStatus.EXECUTED)]),
            ExpectedSuiteReporting(sub3, []),
            ExpectedSuiteReporting(root, [(tc_executed_root, TestCaseProcessingStatus.EXECUTED)]),
        ]
        suite_hierarchy_reader = ReaderThatGivesConstantSuite(root)
        executor = Executor(str_std_out_files.stdout_files,
                            suite_hierarchy_reader,
                            reporter_factory,
                            DepthFirstEnumerator(),
                            test_case_processor,
                            pathlib.Path('root-suite-file'))
        # ACT #
        exit_code = executor.execute()
        # ASSERT #
        check_exit_code_and_empty_stdout(self,
                                         ExecutionTracingCompleteSuiteReporter.VALID_SUITE_EXIT_CODE,
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


class TestCaseProcessorThatRaisesUnconditionally(test_case_processing.TestCaseProcessor):
    def apply(self, test_case: structure.TestCase) -> TestCaseProcessingResult:
        raise NotImplementedError()


class TestCaseProcessorThatGivesConstant(test_case_processing.TestCaseProcessor):
    def __init__(self,
                 result: TestCaseProcessingResult):
        self.result = result

    def apply(self, test_case: structure.TestCase) -> TestCaseProcessingResult:
        return self.result


class TestCaseProcessorThatGivesConstantPerCase(test_case_processing.TestCaseProcessor):
    def __init__(self,
                 test_case_id_2_result: dict):
        """
        :param test_case_id_2_result: int -> TestCaseProcessingResult
        :return:
        """
        self.test_case_id_2_result = test_case_id_2_result

    def apply(self, test_case: structure.TestCase) -> TestCaseProcessingResult:
        return self.test_case_id_2_result[id(test_case)]


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


class EventType(enum.Enum):
    """
    Type for tracking sequence of invocations of methods of SubSuiteReporter.
    """
    SUITE_BEGIN = 1
    CASE_BEGIN = 2
    CASE_END = 3
    SUITE_END = 4


class ExecutionTracingSubSuiteReporter(reporting.SubSuiteReporter):
    def __init__(self,
                 sub_suite: structure.TestSuite):
        self.sub_suite = sub_suite
        self.event_type_list = []
        self.case_begin_list = []
        self.case_end_list = []

    def suite_begin(self):
        self.event_type_list.append(EventType.SUITE_BEGIN)

    def suite_end(self):
        self.event_type_list.append(EventType.SUITE_END)

    def case_begin(self, case: TestCase):
        self.event_type_list.append(EventType.CASE_BEGIN)
        self.case_begin_list.append(case)

    def case_end(self,
                 case: structure.TestCase,
                 result: test_case_processing.TestCaseProcessingResult):
        self.event_type_list.append(EventType.CASE_END)
        self.case_end_list.append((case, result))


class ExecutionTracingCompleteSuiteReporter(reporting.CompleteSuiteReporter):
    VALID_SUITE_EXIT_CODE = 72
    INVALID_SUITE_EXIT_CODE = 87

    def __init__(self):
        self.sub_suite_reporters = []

    def new_sub_suite_reporter(self, sub_suite: structure.TestSuite) -> reporting.SubSuiteReporter:
        reporter = ExecutionTracingSubSuiteReporter(sub_suite)
        self.sub_suite_reporters.append(reporter)
        return reporter

    def valid_suite_exit_code(self) -> int:
        return self.VALID_SUITE_EXIT_CODE

    def invalid_suite_exit_code(self) -> int:
        return self.INVALID_SUITE_EXIT_CODE


class ExecutionTracingReporterFactory(reporting.ReporterFactory):
    def __init__(self):
        self.complete_suite_reporter = ExecutionTracingCompleteSuiteReporter()

    def new_reporter(self, std_output_files: output.StdOutputFiles) -> reporting.CompleteSuiteReporter:
        return self.complete_suite_reporter


class ExpectedSuiteReporting(tuple):
    def __new__(cls,
                test_suite: structure.TestSuite,
                case_and_result_status_list: list):
        """
        :param case_and_result_status_list: [(TestCase, TestCaseProcessingStatus)]
        """
        return tuple.__new__(cls, (test_suite, case_and_result_status_list))

    @staticmethod
    def check_list(put: unittest.TestCase,
                   expected: list,
                   actual: ExecutionTracingCompleteSuiteReporter):
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
              sr: ExecutionTracingSubSuiteReporter,
              msg_header=''):
        put.assertIs(self.suite,
                     sr.sub_suite,
                     msg_header + 'Suite instance')
        put.assertEqual(len(self.case_and_result_status_list),
                        len(sr.case_begin_list),
                        msg_header + 'Number of invocations of case-begin')
        put.assertEqual(len(self.case_and_result_status_list),
                        len(sr.case_end_list),
                        msg_header + 'Number of invocations of case-end')
        for (exp_case, exp_status), begin_case, (end_case, end_proc_result) in zip(self.case_and_result_status_list,
                                                                                   sr.case_begin_list,
                                                                                   sr.case_end_list):
            put.assertIs(exp_case,
                         begin_case,
                         msg_header + 'Registered TestCase instance for case-begin')
            put.assertIs(exp_case,
                         end_case,
                         msg_header + 'Registered TestCase instance for case-end')
            put.assertIs(exp_status,
                         end_proc_result.status,
                         msg_header + 'Registered status instance for case-end')

        self._check_invokation_sequence(put, sr, msg_header)

    def _check_invokation_sequence(self,
                                   put: unittest.TestCase,
                                   sr: ExecutionTracingSubSuiteReporter,
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


DUMMY_EDS = ExecutionDirectoryStructure('test-root-dir')

FULL_RESULT_PASS = new_pass(DUMMY_EDS)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestError))
    ret_val.addTest(unittest.makeSuite(TestReturnValueFromTestCaseProcessor))
    ret_val.addTest(unittest.makeSuite(TestComplexSuite))
    return ret_val


if __name__ == '__main__':
    unittest.main()
