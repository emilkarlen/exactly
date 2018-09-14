import pathlib
import unittest
from typing import List

from exactly_lib.cli.definitions import exit_codes
from exactly_lib.util.cli_syntax.short_and_long_option_syntax import long_syntax
from exactly_lib_test.default.test_resources.internal_main_program_runner import \
    main_program_runner_with_default_setup__in_same_process
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_dir
from exactly_lib_test.test_resources.main_program import main_program_check_base as mpr_check
from exactly_lib_test.test_resources.main_program.main_program_check_base import SetupWithJustMainProgramRunner, \
    SetupWithTmpCwdDirContents
from exactly_lib_test.test_resources.main_program.main_program_check_for_test_case import \
    SetupWithoutPreprocessorAndTestActor
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.process import SubProcessResult, SubProcessResultInfo
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.process_result_assertions import is_result_for_empty_stdout
from exactly_lib_test.test_resources.value_assertions.process_result_info_assertions import \
    is_process_result_for_exit_code


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    tests_without_preprocessor = [
        InvalidCommandLineOptionShouldExitWithInvalidUsageStatus(),
    ]
    tests_with_just_main_program_runner = [
        TestCaseFileDoesNotExistShouldExitWithInvalidUsageStatus(),
    ]
    the_tests_for_setup_with_tmp_cwd = [
        TestCaseFileIsADirectoryShouldExitWithInvalidUsageStatus(),
    ]

    ret_val = unittest.TestSuite()
    ret_val.addTest(
        mpr_check.tests_for_setup_without_preprocessor(tests_without_preprocessor, main_program_runner))
    ret_val.addTest(
        mpr_check.tests_for_setup_with_just_main_program_runner(tests_with_just_main_program_runner,
                                                                main_program_runner))
    ret_val.addTest(
        mpr_check.tests_for_setup_with_tmp_cwd(the_tests_for_setup_with_tmp_cwd, main_program_runner))
    return ret_val


def suite() -> unittest.TestSuite:
    return suite_for(main_program_runner_with_default_setup__in_same_process())


class InvalidCommandLineOptionShouldExitWithInvalidUsageStatus(SetupWithoutPreprocessorAndTestActor):
    def additional_arguments(self) -> List[str]:
        return [long_syntax('invalid-option-that-should-cause-failure')]

    def expected_result(self) -> asrt.ValueAssertion[SubProcessResultInfo]:
        return is_process_result_for_exit_code(exit_codes.EXIT_INVALID_USAGE)

    def test_case(self) -> str:
        return ''


class TestCaseFileDoesNotExistShouldExitWithInvalidUsageStatus(SetupWithJustMainProgramRunner):
    def arguments(self) -> List[str]:
        return ['name-of-non-existing-test.case']

    def check(self,
              put: unittest.TestCase,
              actual_result: SubProcessResult):
        expectation = is_result_for_empty_stdout(exit_codes.EXIT_INVALID_USAGE)
        expectation.apply_without_message(put, actual_result)


class TestCaseFileIsADirectoryShouldExitWithInvalidUsageStatus(SetupWithTmpCwdDirContents):
    file_name = 'test-case-file-argument.case'

    def arguments(self, tmp_cwd_dir_path: pathlib.Path) -> List[str]:
        return ['name-of-non-existing-test.case']

    def file_structure(self, tmp_cwd_dir_path: pathlib.Path) -> DirContents:
        return DirContents([empty_dir(self.file_name)])

    def check(self,
              put: unittest.TestCase,
              tmp_cwd_dir_path: pathlib.Path,
              actual_result: SubProcessResult):
        expectation = is_result_for_empty_stdout(exit_codes.EXIT_INVALID_USAGE)
        expectation.apply_without_message(put, actual_result)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
