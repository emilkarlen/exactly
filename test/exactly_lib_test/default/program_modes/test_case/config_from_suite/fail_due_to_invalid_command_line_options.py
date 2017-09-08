import pathlib
import unittest

from exactly_lib.cli.cli_environment import exit_codes
from exactly_lib.cli.cli_environment.exit_codes import EXIT_INVALID_USAGE
from exactly_lib_test.default.program_modes.test_case.config_from_suite.test_resources import cli_args_for
from exactly_lib_test.default.test_resources.internal_main_program_runner import \
    main_program_runner_with_default_setup__in_same_process
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file
from exactly_lib_test.test_resources.main_program import main_program_check_base as mpr_check
from exactly_lib_test.test_resources.main_program.main_program_check_for_test_case import \
    SetupWithoutPreprocessorAndTestActor
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as asrt_process_result
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.process_result_info_assertions import \
    is_process_result_for_exit_code


def suite_for(mpr: MainProgramRunner) -> unittest.TestSuite:
    tests_with_just_main_program_runner = [
        WhenNeitherTestSuiteNorTestCaseFileExistsResultShouldBeFileAccessError(),
    ]

    the_tests_for_setup_with_tmp_cwd = [
        WhenTestSuiteExistsButNotTestCaseFileExistsResultShouldBeFileAccessError(),
        WhenTestSuiteFileDoNotExistAndTestCaseFileExistsResultShouldBeFileAccessError(),
    ]

    ret_val = unittest.TestSuite()

    ret_val.addTest(
        mpr_check.tests_for_setup_with_just_main_program_runner(tests_with_just_main_program_runner, mpr))

    ret_val.addTest(
        mpr_check.tests_for_setup_with_tmp_cwd(the_tests_for_setup_with_tmp_cwd, mpr))

    return ret_val


def _suite() -> unittest.TestSuite:
    return suite_for(main_program_runner_with_default_setup__in_same_process())


class InvalidCommandLineOptionShouldExitWithInvalidUsageStatus(SetupWithoutPreprocessorAndTestActor):
    def additional_arguments(self) -> list:
        return ['--invalid-option-that-should-cause-failure']

    def expected_result(self) -> asrt.ValueAssertion:
        return is_process_result_for_exit_code(exit_codes.EXIT_INVALID_USAGE)

    def test_case(self) -> str:
        return ''


class WhenNeitherTestSuiteNorTestCaseFileExistsResultShouldBeFileAccessError(mpr_check.SetupWithJustMainProgramRunner):
    def arguments(self) -> list:
        return cli_args_for('non-existing.suite', 'non-existing.case')

    def check(self,
              put: unittest.TestCase,
              actual_result: SubProcessResult):
        expectation = asrt_process_result.is_result_for_exit_code(EXIT_INVALID_USAGE)
        expectation.apply_without_message(put, actual_result)


class WhenTestSuiteExistsButNotTestCaseFileExistsResultShouldBeFileAccessError(mpr_check.SetupWithTmpCwdDirContents):
    name_of_test_suite = 'test.suite'
    name_of_test_case = 'test.case'

    def file_structure(self, tmp_cwd_dir_path: pathlib.Path) -> DirContents:
        return DirContents([empty_file(self.name_of_test_suite)])

    def arguments(self, tmp_cwd_dir_path: pathlib.Path) -> list:
        return cli_args_for(self.name_of_test_suite, self.name_of_test_case)

    def check(self,
              put: unittest.TestCase,
              tmp_cwd_dir_path: pathlib.Path,
              actual_result: SubProcessResult):
        expectation = asrt_process_result.is_result_for_exit_code(EXIT_INVALID_USAGE)
        expectation.apply_without_message(put, actual_result)


class WhenTestSuiteFileDoNotExistAndTestCaseFileExistsResultShouldBeFileAccessError(
    mpr_check.SetupWithTmpCwdDirContents):
    name_of_test_suite = 'test.suite'
    name_of_test_case = 'test.case'

    def file_structure(self, tmp_cwd_dir_path: pathlib.Path) -> DirContents:
        return DirContents([empty_file(self.name_of_test_case)])

    def arguments(self, tmp_cwd_dir_path: pathlib.Path) -> list:
        return cli_args_for(self.name_of_test_suite, self.name_of_test_case)

    def check(self,
              put: unittest.TestCase,
              tmp_cwd_dir_path: pathlib.Path,
              actual_result: SubProcessResult):
        expectation = asrt_process_result.is_result_for_exit_code(EXIT_INVALID_USAGE)
        expectation.apply_without_message(put, actual_result)


if __name__ == '__main__':
    unittest.TextTestRunner().run(_suite())
