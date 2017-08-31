import pathlib
import unittest

from exactly_lib.cli import main_program
from exactly_lib.cli.cli_environment.common_cli_options import SUITE_COMMAND
from exactly_lib_test.default.test_resources.internal_main_program_runner import \
    main_program_runner_with_default_setup__in_same_process
from exactly_lib_test.test_resources.file_structure import DirContents, File
from exactly_lib_test.test_resources.main_program.main_program_check_base import \
    SetupWithJustMainProgramRunner, tests_for_setup_with_just_main_program_runner
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as asrt_process_result
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_suite.reporters.test_resources.simple_progress_reporter_test_setup_base import \
    SetupWithReplacementOfVariableOutputWithPlaceholders


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    # ret_val.addTest(
    #     tests_for_setup_without_preprocessor(TESTS_WITHOUT_PREPROCESSOR,
    #                                          main_program_runner))
    ret_val.addTest(
        tests_for_setup_with_just_main_program_runner(TESTS_WITH_JUST_MAIN_PROGRAM_RUNNER, main_program_runner))
    return ret_val


def suite_for_running_main_program_internally() -> unittest.TestSuite:
    return suite_for(main_program_runner_with_default_setup__in_same_process())


class InvalidOptions(SetupWithReplacementOfVariableOutputWithPlaceholders):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([File('main.suite', ''), ])

    def additional_arguments(self) -> list:
        return ['--invalid-option-that-should-cause-failure']

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return []

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        return []

    def expected_exit_code(self) -> int:
        return main_program.EXIT_INVALID_USAGE


class TestSuiteFileDoesNotExistShouldExitWithInvalidUsageStatus(SetupWithJustMainProgramRunner):
    def arguments(self) -> list:
        return [SUITE_COMMAND, 'name-of-non-existing-test.suite']

    def check(self,
              put: unittest.TestCase,
              actual_result: SubProcessResult):
        expectation = asrt_process_result.sub_process_result(
            exitcode=asrt.equals(main_program.EXIT_INVALID_USAGE))

        expectation.apply_without_message(put, actual_result)


TESTS_WITHOUT_PREPROCESSOR = [
    InvalidOptions(),
]

TESTS_WITH_JUST_MAIN_PROGRAM_RUNNER = [
    TestSuiteFileDoesNotExistShouldExitWithInvalidUsageStatus(),
]

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite_for_running_main_program_internally())
