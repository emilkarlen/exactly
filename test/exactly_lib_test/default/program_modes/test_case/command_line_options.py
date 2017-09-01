import unittest

from exactly_lib.cli import main_program
from exactly_lib_test.default.test_resources.internal_main_program_runner import \
    main_program_runner_with_default_setup__in_same_process
from exactly_lib_test.test_resources.main_program.main_program_check_base import tests_for_setup_without_preprocessor, \
    SetupWithJustMainProgramRunner, tests_for_setup_with_just_main_program_runner
from exactly_lib_test.test_resources.main_program.main_program_check_for_test_case import \
    SetupWithoutPreprocessorAndTestActor
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.process_result_assertions import is_result_for_exit_code
from exactly_lib_test.test_resources.value_assertions.process_result_info_assertions import \
    is_process_result_for_exit_code


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    tests_without_preprocessor = [
        InvalidCommandLineOptionShouldExitWithInvalidUsageStatus(),
    ]
    tests_with_just_main_program_runner = [
        TestCaseFileDoesNotExistShouldExitWithInvalidUsageStatus(),
    ]
    ret_val = unittest.TestSuite()
    ret_val.addTest(tests_for_setup_without_preprocessor(tests_without_preprocessor, main_program_runner))
    ret_val.addTest(
        tests_for_setup_with_just_main_program_runner(tests_with_just_main_program_runner, main_program_runner))
    return ret_val


def suite() -> unittest.TestSuite:
    return suite_for(main_program_runner_with_default_setup__in_same_process())


class InvalidCommandLineOptionShouldExitWithInvalidUsageStatus(SetupWithoutPreprocessorAndTestActor):
    def additional_arguments(self) -> list:
        return ['--invalid-option-that-should-cause-failure']

    def expected_result(self) -> asrt.ValueAssertion:
        return is_process_result_for_exit_code(main_program.EXIT_INVALID_USAGE)

    def test_case(self) -> str:
        return ''


class TestCaseFileDoesNotExistShouldExitWithInvalidUsageStatus(SetupWithJustMainProgramRunner):
    def arguments(self) -> list:
        return ['name-of-non-existing-test.case']

    def check(self,
              put: unittest.TestCase,
              actual_result: SubProcessResult):
        expectation = is_result_for_exit_code(main_program.EXIT_INVALID_USAGE)
        expectation.apply_without_message(put, actual_result)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
