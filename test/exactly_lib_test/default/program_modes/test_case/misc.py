import pathlib
import shutil
import unittest

from exactly_lib.cli import main_program
from exactly_lib.cli.cli_environment.program_modes.test_case import exit_values
from exactly_lib.cli.cli_environment.program_modes.test_case.command_line_options import \
    OPTION_FOR_EXECUTING_ACT_PHASE, OPTION_FOR_KEEPING_SANDBOX_DIRECTORY
from exactly_lib.execution import environment_variables
from exactly_lib.section_document.syntax import section_header
from exactly_lib.test_case import phase_identifier, sandbox_directory_structure
from exactly_lib.util.string import lines_content
from exactly_lib_test.default.test_resources.internal_main_program_runner import \
    run_via_main_program_internally_with_default_setup
from exactly_lib_test.default.test_resources.test_case_file_elements import phase_header_line
from exactly_lib_test.test_case.sandbox_directory_structure import \
    is_execution_directory_structure_after_execution
from exactly_lib_test.test_resources.cli_main_program_via_shell_utils.run import \
    contents_of_file
from exactly_lib_test.test_resources.file_checks import FileChecker
from exactly_lib_test.test_resources.main_program.main_program_check_base import tests_for_setup_without_preprocessor
from exactly_lib_test.test_resources.main_program.main_program_check_for_test_case import \
    SetupWithoutPreprocessorAndTestActor
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.process import SubProcessResult, \
    SubProcessResultInfo
from exactly_lib_test.test_resources.value_assertions import value_assertion as va, process_result_info_assertions
from exactly_lib_test.test_resources.value_assertions.process_result_info_assertions import \
    process_result_for_exit_value, \
    is_process_result_for_exit_code


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(tests_for_setup_without_preprocessor(MISC_TESTS, main_program_runner))
    ret_val.addTest(tests_for_setup_without_preprocessor(SPECIAL_EXECUTION_CONFIGURATIONS_TESTS, main_program_runner))
    return ret_val


def suite() -> unittest.TestSuite:
    return suite_for(run_via_main_program_internally_with_default_setup())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class InvalidCommandLineOptionShouldExitWithInvalidUsageStatus(SetupWithoutPreprocessorAndTestActor):
    def additional_arguments(self) -> list:
        return ['--invalid-option-that-should-cause-failure']

    def expected_result(self) -> va.ValueAssertion:
        return is_process_result_for_exit_code(main_program.EXIT_INVALID_USAGE)

    def test_case(self) -> str:
        return ''


class EmptyTestCaseShouldPass(SetupWithoutPreprocessorAndTestActor):
    def expected_result(self) -> va.ValueAssertion:
        return process_result_for_exit_value(exit_values.EXECUTION__PASS)

    def test_case(self) -> str:
        return ''


class AllPhasesEmptyShouldPass(SetupWithoutPreprocessorAndTestActor):
    def test_case(self) -> str:
        test_case_lines = [phase_header_line(phase)
                           for phase in phase_identifier.ALL]
        return lines_content(test_case_lines)

    def expected_result(self) -> va.ValueAssertion:
        return process_result_for_exit_value(exit_values.EXECUTION__PASS)


class WhenAPhaseHasInvalidPhaseNameThenExitStatusShouldIndicateThis(SetupWithoutPreprocessorAndTestActor):
    def test_case(self) -> str:
        test_case_lines = [
            section_header('invalid phase name'),
        ]
        return lines_content(test_case_lines)

    def expected_result(self) -> va.ValueAssertion:
        return process_result_for_exit_value(exit_values.NO_EXECUTION__SYNTAX_ERROR)


class FlagForPrintingAndPreservingSandbox(SetupWithoutPreprocessorAndTestActor):
    def test_case(self) -> str:
        return ''

    def additional_arguments(self) -> list:
        return [OPTION_FOR_KEEPING_SANDBOX_DIRECTORY]

    def expected_result(self) -> va.ValueAssertion:
        return process_result_info_assertions.assertion_on_process_result(
            va.And([
                va.sub_component('exit code',
                                 SubProcessResult.exitcode.fget,
                                 va.Equals(exit_values.EXECUTION__PASS.exit_code)),
                AssertStdoutIsNameOfExistingSandboxDirectory(),
            ]))


class OutputAndExitCodeFromActPhaseIsEmittedAsResultWhenOptionForExecutingActPhaseIsGiven(
    SetupWithoutPreprocessorAndTestActor):
    def additional_arguments(self) -> list:
        return [OPTION_FOR_EXECUTING_ACT_PHASE]

    def test_case(self) -> str:
        test_case_source = """
[act]
import os
import sys
sys.stdout.write("output to stdout")
sys.stderr.write("output to stderr\\n")
sys.exit(72)
"""
        return test_case_source

    def expected_result(self) -> va.ValueAssertion:
        exit_code = 72
        std_out = 'output to stdout'
        std_err = 'output to stderr\n'
        return process_result_info_assertions.assertion_on_process_result(
            va.And([
                va.sub_component('exit code',
                                 SubProcessResult.exitcode.fget,
                                 va.Equals(exit_code)),
                va.sub_component('stdout',
                                 SubProcessResult.stdout.fget,
                                 va.Equals(std_out)),
                va.sub_component('stderr',
                                 SubProcessResult.stderr.fget,
                                 va.Equals(std_err)),
            ])
        )


class AssertStdoutIsNameOfExistingSandboxDirectory(va.ValueAssertion):
    def apply(self,
              put: unittest.TestCase,
              value: SubProcessResult,
              message_builder: va.MessageBuilder = va.MessageBuilder()):
        actual_eds_directory = _get_printed_eds_or_fail(put, value)
        actual_eds_path = pathlib.Path(actual_eds_directory)
        if actual_eds_path.exists():
            if actual_eds_path.is_dir():
                is_execution_directory_structure_after_execution(
                    FileChecker(put, 'Not an sandbox directory structure'),
                    actual_eds_directory)
                _remove_if_is_directory(actual_eds_directory)
            else:
                put.fail('Output from program is not the sandbox (not a directory): "%s"' % actual_eds_directory)
        else:
            put.fail('The output from the program is not the sandbox: "%s"' % actual_eds_directory)


class EnvironmentVariablesAreSetCorrectly(SetupWithoutPreprocessorAndTestActor):
    def additional_arguments(self) -> list:
        return [OPTION_FOR_KEEPING_SANDBOX_DIRECTORY]

    def test_case(self) -> str:
        test_case_source_lines = [
            '[act]',
            'import os',
            _print_variable_name__equals__variable_value(environment_variables.ENV_VAR_HOME),
            _print_variable_name__equals__variable_value(environment_variables.ENV_VAR_ACT),
            _print_variable_name__equals__variable_value(environment_variables.ENV_VAR_TMP),
        ]
        return lines_content(test_case_source_lines)

    def expected_result(self) -> va.ValueAssertion:
        return va.And([
            process_result_info_assertions.is_process_result_for_exit_code(exit_values.EXECUTION__PASS.exit_code),
            ExpectedTestEnvironmentVariablesAreSetCorrectlyVa(),
        ])


class ExpectedTestEnvironmentVariablesAreSetCorrectlyVa(va.ValueAssertion):
    def apply(self,
              put: unittest.TestCase,
              value: SubProcessResultInfo,
              message_builder: va.MessageBuilder = va.MessageBuilder()):
        actual_eds_directory = _get_printed_eds_or_fail(put, value.sub_process_result)
        eds = sandbox_directory_structure.ExecutionDirectoryStructure(actual_eds_directory)
        actually_printed_variables = _get_act_output_to_stdout(eds).splitlines()
        expected_printed_variables = [
            '%s=%s' % (environment_variables.ENV_VAR_HOME, str(value.file_argument.parent)),
            '%s=%s' % (environment_variables.ENV_VAR_ACT, str(eds.act_dir)),
            '%s=%s' % (environment_variables.ENV_VAR_TMP, str(eds.tmp.user_dir)),
        ]
        put.assertEqual(expected_printed_variables,
                        actually_printed_variables,
                        'Environment variables printed by the act script')
        _remove_if_is_directory(actual_eds_directory)


def _remove_if_is_directory(actual_eds_directory: str):
    actual_eds_path = pathlib.Path(actual_eds_directory)
    if actual_eds_path.is_dir():
        shutil.rmtree(actual_eds_directory)


def _get_printed_eds_or_fail(put: unittest.TestCase, actual: SubProcessResult) -> str:
    printed_lines = actual.stdout.splitlines()
    put.assertEqual(1,
                    len(printed_lines),
                    'Number of printed printed lines should be exactly 1')
    actual_eds_directory = printed_lines[0]
    return actual_eds_directory


def _print_variable_name__equals__variable_value(variable_name: str) -> str:
    return 'print("%s=" + os.environ["%s"])' % (variable_name, variable_name)


def _get_act_output_to_stdout(eds: sandbox_directory_structure.ExecutionDirectoryStructure) -> str:
    return contents_of_file(eds.result.stdout_file)


SPECIAL_EXECUTION_CONFIGURATIONS_TESTS = [
    FlagForPrintingAndPreservingSandbox(),
    OutputAndExitCodeFromActPhaseIsEmittedAsResultWhenOptionForExecutingActPhaseIsGiven(),
]

MISC_TESTS = [
    InvalidCommandLineOptionShouldExitWithInvalidUsageStatus(),
    WhenAPhaseHasInvalidPhaseNameThenExitStatusShouldIndicateThis(),
    EnvironmentVariablesAreSetCorrectly(),
]
