import unittest

from shellcheck_lib.cli.main_program import SUITE_COMMAND, HELP_COMMAND
from shellcheck_lib_test.test_resources.cli_main_program_via_shell_utils.program_modes.test_case import \
    TestCaseFileArgumentArrangement, SubProcessResultExpectation, invalid_usage, TestCaseBase
from shellcheck_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner


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
