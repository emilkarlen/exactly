import unittest

from shellcheck_lib.cli.main_program import EXIT_INVALID_USAGE, SUITE_COMMAND, HELP_COMMAND
from shellcheck_lib_test.test_resources.file_utils import tmp_file_containing
from shellcheck_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from shellcheck_lib_test.test_resources.process import SubProcessResultInfo


class TestCaseFileArgumentArrangement:
    def __init__(self,
                 test_case_contents: str = '',
                 arguments_before_file_argument: iter = ()):
        self.test_case_contents = test_case_contents
        self.arguments_before_file_argument = arguments_before_file_argument


class SubProcessResultExpectation:
    def apply(self,
              put: unittest.TestCase,
              actual: SubProcessResultInfo):
        raise NotImplementedError()


def run_test(arrangement: TestCaseFileArgumentArrangement,
             expectation: SubProcessResultExpectation,
             main_program_runner: MainProgramRunner,
             put: unittest.TestCase):
    with tmp_file_containing(arrangement.test_case_contents) as test_case_file_path:
        arguments = list(arrangement.arguments_before_file_argument) + [str(test_case_file_path)]
        sub_process_result = main_program_runner.run(put, arguments)
        sub_process_result_info = SubProcessResultInfo(test_case_file_path, sub_process_result)
        expectation.apply(put, sub_process_result_info)


class ExitCodeAndStdOutExpectation(SubProcessResultExpectation):
    def __init__(self,
                 exit_code: int,
                 std_out: str):
        self.exit_code = exit_code
        self.std_out = std_out

    def apply(self,
              put: unittest.TestCase,
              actual: SubProcessResultInfo):
        put.assertEqual(self.exit_code,
                        actual.sub_process_result.exitcode,
                        'Exit code')
        put.assertEqual(self.std_out,
                        actual.sub_process_result.stdout,
                        'stdout')


def invalid_usage() -> SubProcessResultExpectation:
    return ExitCodeAndStdOutExpectation(exit_code=EXIT_INVALID_USAGE,
                                        std_out='')


class TestCaseBase(unittest.TestCase):
    def __init__(self, main_program_runner: MainProgramRunner):
        super().__init__()
        self.main_program_runner = main_program_runner

    def runTest(self):
        run_test(self._arrangement(),
                 self._expectation(),
                 self.main_program_runner,
                 self)

    def _arrangement(self) -> TestCaseFileArgumentArrangement:
        raise NotImplementedError()

    def _expectation(self) -> SubProcessResultExpectation:
        raise NotImplementedError()

    def shortDescription(self):
        return str(type(self))


class TestExitStatusWithInvalidInvokationForTestCase(TestCaseBase):
    def _arrangement(self) -> TestCaseFileArgumentArrangement:
        return TestCaseFileArgumentArrangement(
            arguments_before_file_argument=('--illegal-flag-42847920189',))

    def _expectation(self) -> SubProcessResultExpectation:
        return invalid_usage()


class TestExitStatusWithInvalidInvokationForTestSuite(TestCaseBase):
    def _arrangement(self) -> TestCaseFileArgumentArrangement:
        return TestCaseFileArgumentArrangement(
            arguments_before_file_argument=(SUITE_COMMAND, '--illegal-flag-42847920189'))

    def _expectation(self) -> SubProcessResultExpectation:
        return invalid_usage()


class TestExitStatusWithInvalidInvokationForHelp(TestCaseBase):
    def _arrangement(self) -> TestCaseFileArgumentArrangement:
        return TestCaseFileArgumentArrangement(
            arguments_before_file_argument=(HELP_COMMAND, '--illegal-flag-42847920189'))

    def _expectation(self) -> SubProcessResultExpectation:
        return invalid_usage()


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.TestSuite([
        TestExitStatusWithInvalidInvokationForTestCase(main_program_runner),
        TestExitStatusWithInvalidInvokationForTestSuite(main_program_runner),
        TestExitStatusWithInvalidInvokationForHelp(main_program_runner),
    ]))
    return ret_val
