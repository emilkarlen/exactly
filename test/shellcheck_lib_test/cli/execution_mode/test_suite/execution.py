import pathlib
import unittest

from shellcheck_lib.cli.execution_mode.test_suite import settings
from shellcheck_lib.cli.execution_mode.test_suite.execution import Executor, TestCaseReader
from shellcheck_lib.execution.result import FullResult
from shellcheck_lib.general import line_source
from shellcheck_lib.general import output
from shellcheck_lib.test_case.test_case_struct import TestCase
from shellcheck_lib.test_suite import structure
from shellcheck_lib.test_suite.enumeration import DepthFirstEnumerator
from shellcheck_lib.test_suite.parse import SuiteSyntaxError
from shellcheck_lib.test_suite import reporting
from shellcheck_lib.test_suite.suite_hierarchy_reading import SuiteHierarchyReader
from shellcheck_lib_test.util.str_std_out_files import StringStdOutFiles


class TestError(unittest.TestCase):
    def test_error_when_reading_suite_structure(self):
        # ARRANGE #
        str_std_out_files = StringStdOutFiles()
        suite_hierarchy_reader = ReaderThatRaisesParseError()
        reporter_factory = ExecutionTracingReporterFactory()
        execution_settings = settings.Settings(reporter_factory,
                                               DepthFirstEnumerator(),
                                               pathlib.Path('root-suite-file'))
        executor = Executor(str_std_out_files.stdout_files,
                            suite_hierarchy_reader,
                            TestCaseReaderThatRaisesUnconditionally(),
                            execution_settings)
        # ACT #
        exit_code = executor.execute()
        # ASSERT #
        check_exit_code_and_empty_stdout(self,
                                         ExecutionTracingCompleteSuiteReporter.INVALID_SUITE_EXIT_CODE,
                                         exit_code,
                                         str_std_out_files)
        ExpectedSuiteReporting.check_list(self, [], reporter_factory.complete_suite_reporter)


class TestSuiteWithTestCasesThatPasses(unittest.TestCase):
    def test_single_suite_with_no_cases(self):
        # ARRANGE #
        str_std_out_files = StringStdOutFiles()
        # sub11 = TestSuite(pathlib.Path('11'), [], [], [])
        # sub12 = TestSuite(pathlib.Path('12'), [], [], [])
        # sub1 = TestSuite(pathlib.Path('1'), [], [sub11, sub12], [])
        # sub21 = TestSuite(pathlib.Path('21'), [], [], [])
        # sub2 = TestSuite(pathlib.Path('2'), [], [sub21], [])
        # root = TestSuite(pathlib.Path('root'), [], [sub1, sub2], [])
        root = structure.TestSuite(pathlib.Path('root'), [], [], [])
        suite_hierarchy_reader = ReaderThatGivesConstantSuite(root)
        reporter_factory = ExecutionTracingReporterFactory()
        execution_settings = settings.Settings(reporter_factory,
                                               DepthFirstEnumerator(),
                                               pathlib.Path('root-suite-file'))
        executor = Executor(str_std_out_files.stdout_files,
                            suite_hierarchy_reader,
                            TestCaseReaderThatRaisesUnconditionally(),
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
            [ExpectedSuiteReporting(root, [])],
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


class TestCaseReaderThatRaisesUnconditionally(TestCaseReader):
    def __call__(self, path: pathlib.Path) -> TestCase:
        raise NotImplementedError()


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

    def case_end(self, case: TestCase, full_result: FullResult):
        self.case_end_list.append((case, full_result))


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
        :param case_and_result_status_list: [(TestCase, FullResultStatus)]
        """
        return tuple.__new__(cls, (test_suite, case_and_result_status_list))

    @staticmethod
    def check_list(put: unittest.TestCase,
                   expected: list,
                   actual: ExecutionTracingCompleteSuiteReporter):
        """
        :param expected: [ExpectedSuiteReporting]
        """
        i = 0
        for e, a in zip(expected, actual.sub_suite_reporters):
            e.check(put, a, 'Suite at index ' + str(i) + ': ')
            i += 1
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
        for (exp_case, exp_status), begin_case, (end_case, end_full_result) in zip(self.case_and_result_status_list,
                                                                                   sr.case_begin_list,
                                                                                   sr.case_end_list):
            put.assertIs(exp_case,
                         begin_case,
                         msg_header + 'Registered TestCase instance for case-begin')
            put.assertIs(exp_case,
                         end_case,
                         msg_header + 'Registered TestCase instance for case-end')
            put.assertIs(exp_status,
                         end_full_result.status,
                         msg_header + 'Registered status instance for case-end')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestError))
    ret_val.addTest(unittest.makeSuite(TestSuiteWithTestCasesThatPasses))
    return ret_val


if __name__ == '__main__':
    unittest.main()
