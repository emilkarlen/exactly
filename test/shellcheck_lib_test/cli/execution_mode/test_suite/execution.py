import pathlib
import unittest

from shellcheck_lib.cli.execution_mode.test_suite import settings
from shellcheck_lib.cli.execution_mode.test_suite.execution import Executor
from shellcheck_lib.execution.result import FullResult
from shellcheck_lib.general import line_source
from shellcheck_lib.general import output
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
                            execution_settings)
        # ACT #
        exit_code = executor.execute()
        # ASSERT #
        self.assertEqual(ExecutionTracingCompleteSuiteReporter.INVALID_SUITE_EXIT_CODE,
                         exit_code,
                         'Exit Code')
        self.assertEqual(
            [],
            reporter_factory.complete_suite_reporter.sub_suite_reporters,
            'Sub-suite reporters')

        self.assertEqual(
            '',
            str_std_out_files.stdout_contents,
            'Output on stdout')


class ReaderThatRaisesParseError(SuiteHierarchyReader):
    def apply(self, suite_file_path: pathlib.Path) -> structure.TestSuite:
        raise SuiteSyntaxError(suite_file_path,
                               line_source.Line(1, 'line'),
                               'message')


class ExecutionTracingSubSuiteReporter(reporting.SubSuiteReporter):
    def __init__(self):
        self.num_suite_begin_invocations = 0
        self.num_suite_end_invocations = 0
        self.case_begin_invocations = []
        self.case_end_invocations = []

    def suite_begin(self):
        self.num_suite_begin_invocations += 1

    def suite_end(self):
        self.num_suite_end_invocations += 1

    def case_begin(self, case: TestError):
        self.case_begin_invocations.append(case)

    def case_end(self, case: TestError, full_result: FullResult):
        self.case_begin_invocations.append((case, full_result))


class ExecutionTracingCompleteSuiteReporter(reporting.CompleteSuiteReporter):
    VALID_SUITE_EXIT_CODE = 72
    INVALID_SUITE_EXIT_CODE = 87

    def __init__(self):
        self.sub_suite_reporters = []

    def new_sub_suite_reporter(self, sub_suite: structure.TestSuite) -> reporting.SubSuiteReporter:
        reporter = ExecutionTracingSubSuiteReporter()
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


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestError))
    return ret_val


if __name__ == '__main__':
    unittest.main()
