import unittest

from exactly_lib.cli.cli_environment.program_modes.test_case.command_line_options import \
    OPTION_FOR_EXECUTING_ACT_PHASE
from exactly_lib.processing import exit_values
from exactly_lib_test.default.test_resources.internal_main_program_runner import \
    main_program_runner_with_default_setup__in_same_process
from exactly_lib_test.test_resources.main_program.main_program_check_base import tests_for_setup_without_preprocessor
from exactly_lib_test.test_resources.main_program.main_program_check_for_test_case import \
    SetupWithoutPreprocessorAndTestActor
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt, \
    process_result_info_assertions as asrt_process_result_info, \
    process_result_assertions as asrt_process_result


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    tests = [
        WhenValidationFailsThenOutputShouldBeAsWithoutActOption(),
        WhenParseFailsThenOutputShouldBeAsWithoutActOption(),
        OutputAndExitCodeFromActPhaseIsEmittedWhenTestCaseExecutesSuccessfully(),
    ]
    return tests_for_setup_without_preprocessor(tests, main_program_runner)


def suite() -> unittest.TestSuite:
    return suite_for(main_program_runner_with_default_setup__in_same_process())


class OutputAndExitCodeFromActPhaseIsEmittedWhenTestCaseExecutesSuccessfully(SetupWithoutPreprocessorAndTestActor):
    exit_code = 72
    std_out = 'output to stdout'
    std_err = 'output to stderr'

    def additional_arguments(self) -> list:
        return [OPTION_FOR_EXECUTING_ACT_PHASE]

    def test_case(self) -> str:
        test_case_source = """\
[act]
import os
import sys
sys.stdout.write("{output_to_stdout}")
sys.stderr.write("{output_to_stderr}")
sys.exit({exit_code})
""".format(
            exit_code=self.exit_code,
            output_to_stdout=self.std_out,
            output_to_stderr=self.std_err,
        )
        return test_case_source

    def expected_result(self) -> asrt.ValueAssertion:
        return asrt_process_result_info.assertion_on_process_result(
            asrt_process_result.sub_process_result(
                exitcode=asrt.Equals(self.exit_code),
                stdout=asrt.Equals(self.std_out),
            ))


class WhenParseFailsThenOutputShouldBeAsWithoutActOption(SetupWithoutPreprocessorAndTestActor):
    def additional_arguments(self) -> list:
        return [OPTION_FOR_EXECUTING_ACT_PHASE]

    def test_case(self) -> str:
        test_case_source = """\
[not_the_name_of_a_test_case_phase]
"""
        return test_case_source

    def expected_result(self) -> asrt.ValueAssertion:
        return asrt_process_result_info.assertion_on_process_result(
            asrt_process_result.is_result_for_exit_value(exit_values.NO_EXECUTION__SYNTAX_ERROR))


class WhenValidationFailsThenOutputShouldBeAsWithoutActOption(SetupWithoutPreprocessorAndTestActor):
    def additional_arguments(self) -> list:
        return [OPTION_FOR_EXECUTING_ACT_PHASE]

    def test_case(self) -> str:
        test_case_source = """\
[setup]

install non-existing-file

[act]

ignored action
"""
        return test_case_source

    def expected_result(self) -> asrt.ValueAssertion:
        return asrt_process_result_info.assertion_on_process_result(
            asrt_process_result.is_result_for_exit_value(exit_values.EXECUTION__VALIDATE))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
