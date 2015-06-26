import pathlib
from pathlib import Path
import unittest

from shellcheck_lib.cli.execution_mode.test_suite import settings
from shellcheck_lib.cli.execution_mode.test_suite.execution import Executor
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
    TestCaseReadingError
from shellcheck_lib_test.util.str_std_out_files import StringStdOutFiles


class TestError(unittest.TestCase):
    def test_error_when_reading_suite_structure(self):
        # ARRANGE #
        str_std_out_files = StringStdOutFiles()
        suite_hierarchy_reader = ReaderThatRaisesParseError()
        reporter_factory = ExecutionTracingReporterFactory()
        execution_settings = settings.Settings(reporter_factory,
                                               DepthFirstEnumerator(),
                                               Path('root-suite-file'))
        executor = Executor(str_std_out_files.stdout_files,
                            suite_hierarchy_reader,
                            TestCaseProcessorThatRaisesUnconditionally(),
                            execution_settings)
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
        execution_settings = settings.Settings(reporter_factory,
                                               DepthFirstEnumerator(),
                                               pathlib.Path('root-suite-file'))
        executor = Executor(str_std_out_files.stdout_files,
                            suite_hierarchy_reader,
                            TestCaseProcessorThatRaisesUnconditionally(),
                            execution_settings)
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
        result = test_case_processing.new_reading_error(TestCaseReadingError.FILE_ACCESS_ERROR)
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
        execution_settings = settings.Settings(reporter_factory,
                                               DepthFirstEnumerator(),
                                               pathlib.Path('root-suite-file'))
        executor = Executor(str_std_out_files.stdout_files,
                            suite_hierarchy_reader,
                            TestCaseProcessorThatGivesConstant(result),
                            execution_settings)
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
        tc_read_error = structure.TestCase(Path('read error'))
        tc_executed = structure.TestCase(Path('executed'))
        root = structure.TestSuite(
            pathlib.Path('root'),
            [],
            [],
            [
                tc_internal_error,
                tc_read_error,
                tc_executed,
            ])
        test_case_processor = TestCaseProcessorThatGivesConstantPerCase({
            id(tc_internal_error): test_case_processing.new_internal_error('message'),
            id(tc_read_error): test_case_processing.new_reading_error(TestCaseReadingError.PARSE_ERROR),
            id(tc_executed): test_case_processing.new_executed(FULL_RESULT_PASS),
        })
        expected_suites = [
            ExpectedSuiteReporting(root,
                                   [
                                       (tc_internal_error, TestCaseProcessingStatus.INTERNAL_ERROR),
                                       (tc_read_error, TestCaseProcessingStatus.READ_ERROR),
                                       (tc_executed, TestCaseProcessingStatus.EXECUTED),
                                   ])
        ]
        suite_hierarchy_reader = ReaderThatGivesConstantSuite(root)
        execution_settings = settings.Settings(reporter_factory,
                                               DepthFirstEnumerator(),
                                               pathlib.Path('root-suite-file'))
        executor = Executor(str_std_out_files.stdout_files,
                            suite_hierarchy_reader,
                            test_case_processor,
                            execution_settings)
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
        execution_settings = settings.Settings(reporter_factory,
                                               DepthFirstEnumerator(),
                                               pathlib.Path('root-suite-file'))
        executor = Executor(str_std_out_files.stdout_files,
                            suite_hierarchy_reader,
                            TestCaseProcessorThatGivesConstantPerCase({}),
                            execution_settings)
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
        tc_read_error_1 = structure.TestCase(Path('read error A'))
        tc_read_error_12 = structure.TestCase(Path('read error 12'))
        tc_executed_11 = structure.TestCase(Path('executed 11'))
        tc_executed_12 = structure.TestCase(Path('executed 12'))
        tc_executed_1 = structure.TestCase(Path('executed 1'))
        tc_executed_2 = structure.TestCase(Path('executed 2'))
        tc_executed_root = structure.TestCase(Path('executed root'))
        test_case_processor = TestCaseProcessorThatGivesConstantPerCase({
            id(tc_internal_error_11): test_case_processing.new_internal_error('message A'),
            id(tc_internal_error_21): test_case_processing.new_internal_error('messageB'),
            id(tc_read_error_1): test_case_processing.new_reading_error(TestCaseReadingError.PARSE_ERROR),
            id(tc_read_error_12): test_case_processing.new_reading_error(TestCaseReadingError.FILE_ACCESS_ERROR),
            id(tc_executed_11): test_case_processing.new_executed(FULL_RESULT_PASS),
            id(tc_executed_12): test_case_processing.new_executed(FULL_RESULT_PASS),
            id(tc_executed_1): test_case_processing.new_executed(FULL_RESULT_PASS),
            id(tc_executed_2): test_case_processing.new_executed(FULL_RESULT_PASS),
            id(tc_executed_root): test_case_processing.new_executed(FULL_RESULT_PASS),
        })
        sub11 = structure.TestSuite(pathlib.Path('11'), [], [], [tc_internal_error_11,
                                                                 tc_executed_11])
        sub12 = structure.TestSuite(pathlib.Path('12'), [], [], [tc_executed_12,
                                                                 tc_read_error_12])
        sub1 = structure.TestSuite(pathlib.Path('1'), [], [sub11, sub12], [tc_read_error_1,
                                                                           tc_executed_1])
        sub21 = structure.TestSuite(pathlib.Path('21'), [], [], [tc_internal_error_21])
        sub2 = structure.TestSuite(pathlib.Path('2'), [], [sub21], [tc_executed_2])
        root = structure.TestSuite(pathlib.Path('root'), [], [sub1, sub2], [tc_executed_root])

        expected_suites = [
            ExpectedSuiteReporting(sub11, [(tc_internal_error_11, TestCaseProcessingStatus.INTERNAL_ERROR),
                                           (tc_executed_11, TestCaseProcessingStatus.EXECUTED)]),
            ExpectedSuiteReporting(sub12, [(tc_executed_12, TestCaseProcessingStatus.EXECUTED),
                                           (tc_read_error_12, TestCaseProcessingStatus.READ_ERROR)]),
            ExpectedSuiteReporting(sub1, [(tc_read_error_1, TestCaseProcessingStatus.READ_ERROR),
                                          (tc_executed_1, TestCaseProcessingStatus.EXECUTED)]),
            ExpectedSuiteReporting(sub21, [(tc_internal_error_21, TestCaseProcessingStatus.INTERNAL_ERROR)]),
            ExpectedSuiteReporting(sub2, [(tc_executed_2, TestCaseProcessingStatus.EXECUTED)]),
            ExpectedSuiteReporting(root, [(tc_executed_root, TestCaseProcessingStatus.EXECUTED)]),
        ]
        suite_hierarchy_reader = ReaderThatGivesConstantSuite(root)
        execution_settings = settings.Settings(reporter_factory,
                                               DepthFirstEnumerator(),
                                               pathlib.Path('root-suite-file'))
        executor = Executor(str_std_out_files.stdout_files,
                            suite_hierarchy_reader,
                            test_case_processor,
                            execution_settings)
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


class ExecutionTracingSubSuiteReporter(reporting.SubSuiteReporter):
    def __init__(self,
                 sub_suite: structure.TestSuite):
        self.sub_suite = sub_suite
        self.num_suite_begin_invocations = 0
        self.num_suite_end_invocations = 0
        self.case_begin_list = []
        self.case_end_list = []

    def suite_begin(self):
        self.num_suite_begin_invocations += 1

    def suite_end(self):
        self.num_suite_end_invocations += 1

    def case_begin(self, case: TestCase):
        self.case_begin_list.append(case)

    def case_end(self,
                 case: structure.TestCase,
                 result: test_case_processing.TestCaseProcessingResult):
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
        put.assertEqual(1,
                        sr.num_suite_begin_invocations,
                        msg_header + 'Number of invocations of suite-begin')
        put.assertEqual(1,
                        sr.num_suite_end_invocations,
                        msg_header + 'Number of invocations of suite-end')
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
