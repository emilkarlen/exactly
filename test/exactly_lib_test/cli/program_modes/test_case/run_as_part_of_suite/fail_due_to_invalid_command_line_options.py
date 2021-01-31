import pathlib
import unittest
from typing import List

from exactly_lib.cli.definitions import exit_codes
from exactly_lib.cli.definitions.exit_codes import EXIT_INVALID_USAGE
from exactly_lib.util.cli_syntax.short_and_long_option_syntax import long_syntax
from exactly_lib_test.cli.program_modes.test_case.run_as_part_of_suite.test_resources.cli_args import \
    cli_args_for_explicit_suite
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.main_program import main_program_check_base as mpr_check
from exactly_lib_test.test_resources.main_program.main_program_check_for_test_case import \
    SetupWithoutPreprocessorAndTestActor
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.main_program.main_program_runner_via_same_process import \
    RunViaMainProgramInternally
from exactly_lib_test.test_resources.process import SubProcessResult, SubProcessResultInfo
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as asrt_process_result
from exactly_lib_test.test_resources.value_assertions.process_result_info_assertions import \
    is_process_result_for_exit_code
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def suite_for(mpr: MainProgramRunner) -> unittest.TestSuite:
    tests_with_just_main_program_runner = [
        WhenNeitherTestSuiteNorTestCaseFileExistsResultShouldBeInvalidUsageError(),
    ]

    the_tests_for_setup_with_tmp_cwd = [
        WhenTestSuiteExistsButNotTestCaseFileExistsResultShouldBeInvalidUsageError(),
        WhenTestSuiteFileDoNotExistAndTestCaseFileExistsResultShouldBeInvalidUsageError(),
    ]

    ret_val = unittest.TestSuite()

    ret_val.addTest(
        mpr_check.tests_for_setup_with_just_main_program_runner(tests_with_just_main_program_runner, mpr))

    ret_val.addTest(
        mpr_check.tests_for_setup_with_tmp_cwd(the_tests_for_setup_with_tmp_cwd, mpr))

    return ret_val


def _suite() -> unittest.TestSuite:
    return suite_for(RunViaMainProgramInternally())


class InvalidCommandLineOptionShouldExitWithInvalidUsageStatus(SetupWithoutPreprocessorAndTestActor):
    def additional_arguments(self) -> List[str]:
        return [long_syntax('invalid-option-that-should-cause-failure')]

    def expected_result(self) -> Assertion[SubProcessResultInfo]:
        return is_process_result_for_exit_code(exit_codes.EXIT_INVALID_USAGE)

    def test_case(self) -> str:
        return ''


class WhenNeitherTestSuiteNorTestCaseFileExistsResultShouldBeInvalidUsageError(
    mpr_check.SetupWithJustMainProgramRunner):
    def arguments(self) -> List[str]:
        return cli_args_for_explicit_suite('non-existing.suite', 'non-existing.case')

    def check(self,
              put: unittest.TestCase,
              actual_result: SubProcessResult):
        expectation = asrt_process_result.is_result_for_exit_code(EXIT_INVALID_USAGE)
        expectation.apply_without_message(put, actual_result)


class WhenTestSuiteExistsButNotTestCaseFileExistsResultShouldBeInvalidUsageError(mpr_check.SetupWithTmpCwdDirContents):
    name_of_test_suite = 'test.suite'
    name_of_test_case = 'test.case'

    def file_structure(self, tmp_cwd_dir_path: pathlib.Path) -> DirContents:
        return DirContents([File.empty(self.name_of_test_suite)])

    def arguments(self, tmp_cwd_dir_path: pathlib.Path) -> list:
        return cli_args_for_explicit_suite(self.name_of_test_suite, self.name_of_test_case)

    def check(self,
              put: unittest.TestCase,
              tmp_cwd_dir_path: pathlib.Path,
              actual_result: SubProcessResult):
        expectation = asrt_process_result.is_result_for_exit_code(EXIT_INVALID_USAGE)
        expectation.apply_without_message(put, actual_result)


class WhenTestSuiteFileDoNotExistAndTestCaseFileExistsResultShouldBeInvalidUsageError(
    mpr_check.SetupWithTmpCwdDirContents):
    name_of_test_suite = 'test.suite'
    name_of_test_case = 'test.case'

    def file_structure(self, tmp_cwd_dir_path: pathlib.Path) -> DirContents:
        return DirContents([File.empty(self.name_of_test_case)])

    def arguments(self, tmp_cwd_dir_path: pathlib.Path) -> list:
        return cli_args_for_explicit_suite(self.name_of_test_suite, self.name_of_test_case)

    def check(self,
              put: unittest.TestCase,
              tmp_cwd_dir_path: pathlib.Path,
              actual_result: SubProcessResult):
        expectation = asrt_process_result.is_result_for_exit_code(EXIT_INVALID_USAGE)
        expectation.apply_without_message(put, actual_result)


if __name__ == '__main__':
    unittest.TextTestRunner().run(_suite())
