import unittest

from exactly_lib.cli import main_program
from exactly_lib_test.default.test_resources.internal_main_program_runner import \
    main_program_runner_with_default_setup__in_same_process
from exactly_lib_test.test_resources.main_program.main_program_check_base import tests_for_setup_without_preprocessor
from exactly_lib_test.test_resources.main_program.main_program_check_for_test_case import \
    SetupWithoutPreprocessorAndTestActor
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.process_result_info_assertions import \
    is_process_result_for_exit_code


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    tests = [
        InvalidCommandLineOptionShouldExitWithInvalidUsageStatus(),
    ]
    ret_val = unittest.TestSuite()
    ret_val.addTest(tests_for_setup_without_preprocessor(tests, main_program_runner))
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


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
