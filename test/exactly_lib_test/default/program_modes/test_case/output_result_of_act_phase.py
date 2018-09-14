import unittest
from typing import List

from exactly_lib.cli.definitions.program_modes.test_case.command_line_options import \
    OPTION_FOR_EXECUTING_ACT_PHASE
from exactly_lib.common.exit_value import ExitValue
from exactly_lib.processing import exit_values
from exactly_lib.util.std import StdOutputFilesContents
from exactly_lib_test.default.test_resources.internal_main_program_runner import \
    main_program_runner_with_default_setup__in_same_process
from exactly_lib_test.test_resources.main_program.main_program_check_base import tests_for_setup_without_preprocessor
from exactly_lib_test.test_resources.main_program.main_program_check_for_test_case import \
    SetupWithoutPreprocessorAndTestActor
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.process import SubProcessResultInfo, SubProcessResult
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt, \
    process_result_info_assertions as asrt_process_result_info, \
    process_result_assertions as asrt_process_result
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder


def suite_that_requires_main_program_runner_with_default_setup(mpr: MainProgramRunner) -> unittest.TestSuite:
    tests = [
        WhenValidationFailsThenOutputShouldBeAsWithoutActOptionButOnStderr(),
        WhenParseFailsThenOutputShouldBeAsWithoutActOptionButOnStderr(),
        OutputAndExitCodeFromActPhaseIsEmittedWhenTestCaseExecutesSuccessfully(),
        WhenTimeoutThenOutputShouldOutputFromAtcFollowedByErrorReportingOnStderr(),
    ]
    return tests_for_setup_without_preprocessor(tests, mpr)


def suite() -> unittest.TestSuite:
    return suite_that_requires_main_program_runner_with_default_setup(
        main_program_runner_with_default_setup__in_same_process()
    )


class OutputAndExitCodeFromActPhaseIsEmittedWhenTestCaseExecutesSuccessfully(SetupWithoutPreprocessorAndTestActor):
    exit_code = 72
    std_out = 'output to stdout'
    std_err = 'output to stderr'

    def additional_arguments(self) -> List[str]:
        return [OPTION_FOR_EXECUTING_ACT_PHASE]

    def test_case(self) -> str:
        test_case_source = """\
[act]
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

    def expected_result(self) -> asrt.ValueAssertion[SubProcessResultInfo]:
        return asrt_process_result_info.assertion_on_process_result(
            asrt_process_result.sub_process_result(
                exitcode=asrt.equals(self.exit_code),
                stdout=asrt.equals(self.std_out),
            ))


class WhenParseFailsThenOutputShouldBeAsWithoutActOptionButOnStderr(SetupWithoutPreprocessorAndTestActor):
    def additional_arguments(self) -> List[str]:
        return [OPTION_FOR_EXECUTING_ACT_PHASE]

    def test_case(self) -> str:
        test_case_source = """\
[not_the_name_of_a_test_case_phase]
"""
        return test_case_source

    def expected_result(self) -> asrt.ValueAssertion[SubProcessResultInfo]:
        return asrt_process_result_info.assertion_on_process_result(
            StdoutIsEmptyAndStderrIsExitIdentifierFollowedByErrorMessage(exit_values.NO_EXECUTION__SYNTAX_ERROR))


class WhenValidationFailsThenOutputShouldBeAsWithoutActOptionButOnStderr(SetupWithoutPreprocessorAndTestActor):
    def additional_arguments(self) -> List[str]:
        return [OPTION_FOR_EXECUTING_ACT_PHASE]

    def test_case(self) -> str:
        test_case_source = """\
[setup]

copy non-existing-file

[act]

ignored action
"""
        return test_case_source

    def expected_result(self) -> asrt.ValueAssertion[SubProcessResultInfo]:
        return asrt_process_result_info.assertion_on_process_result(
            StdoutIsEmptyAndStderrIsExitIdentifierFollowedByErrorMessage(exit_values.EXECUTION__VALIDATION_ERROR))


class WhenTimeoutThenOutputShouldOutputFromAtcFollowedByErrorReportingOnStderr(SetupWithoutPreprocessorAndTestActor):
    expected_atc_output = StdOutputFilesContents('some output to stdout before taking a nap',
                                                 'some output to stderr before taking a nap')

    def additional_arguments(self) -> List[str]:
        return [OPTION_FOR_EXECUTING_ACT_PHASE]

    def test_case(self) -> str:
        py_src = py_programs.py_pgm_with_stdout_stderr_and_sleep_in_between(
            stdout_output_before_sleep=self.expected_atc_output.out,
            stderr_output_before_sleep=self.expected_atc_output.err,
            stdout_output_after_sleep='just woke up, more output to stdout',
            stderr_output_after_sleep='just woke up, more output to stderr',
            sleep_seconds=4,
            exit_code=0
        )

        test_case_source = """\
[conf]

timeout = 1

[act]

""" + py_src
        return test_case_source

    def expected_result(self) -> asrt.ValueAssertion[SubProcessResultInfo]:
        return asrt_process_result_info.assertion_on_process_result(
            OutputIsCombinationOfInterruptedAtcAndErrorReport(exit_values.EXECUTION__HARD_ERROR,
                                                              self.expected_atc_output)
        )


class OutputIsCombinationOfInterruptedAtcAndErrorReport(asrt.ValueAssertion[SubProcessResult]):
    def __init__(self,
                 expected_exit_value: ExitValue,
                 expected_atc_output: StdOutputFilesContents
                 ):
        self.expected_exit_value = expected_exit_value
        self.expected_atc_output = expected_atc_output

    def apply(self,
              put: unittest.TestCase,
              value: SubProcessResult,
              message_builder: MessageBuilder = MessageBuilder()):
        msg_info = '\nInfo from actual value:\nstdout = "{stdout}"\nstderr="{stderr}"'.format(stdout=value.stdout,
                                                                                              stderr=value.stderr)

        put.assertEqual(self.expected_exit_value.exit_code,
                        value.exitcode,
                        'exit code' + msg_info)

        put.assertEqual(self.expected_atc_output.out,
                        value.stdout,
                        'stdout should be output from ATC' + msg_info)

        expected_initial_contents_of_stderr = (self.expected_atc_output.err +
                                               self.expected_exit_value.exit_identifier)
        actual_initial_contents_of_stderr = value.stderr[:len(expected_initial_contents_of_stderr)]

        put.assertEqual(expected_initial_contents_of_stderr,
                        actual_initial_contents_of_stderr,
                        'stderr should start with output from ATC followed by exit identifier' + msg_info)


class StdoutIsEmptyAndStderrIsExitIdentifierFollowedByErrorMessage(asrt.ValueAssertion[SubProcessResult]):
    def __init__(self,
                 expected_exit_value: ExitValue,
                 ):
        self.expected_exit_value = expected_exit_value

    def apply(self,
              put: unittest.TestCase,
              value: SubProcessResult,
              message_builder: MessageBuilder = MessageBuilder()):
        msg_info = '\nInfo from actual value:\nstdout = "{stdout}"\nstderr="{stderr}"'.format(stdout=value.stdout,
                                                                                              stderr=value.stderr)

        put.assertEqual(self.expected_exit_value.exit_code,
                        value.exitcode,
                        'exit code' + msg_info)

        put.assertEqual('',
                        value.stdout,
                        'stdout should be empty' + msg_info)

        expected_initial_contents_of_stderr = self.expected_exit_value.exit_identifier + '\n'
        actual_initial_contents_of_stderr = value.stderr[:len(expected_initial_contents_of_stderr)]

        put.assertEqual(expected_initial_contents_of_stderr,
                        actual_initial_contents_of_stderr,
                        'stderr should start with exit identifier' + msg_info)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
