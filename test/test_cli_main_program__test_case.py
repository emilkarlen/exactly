import pathlib
import shutil
import unittest

from shellcheck_lib.cli.cli_environment import exit_values
from shellcheck_lib.cli.cli_environment.command_line_options import OPTION_FOR_KEEPING_SANDBOX_DIRECTORY, \
    OPTION_FOR_EXECUTING_ACT_PHASE
from shellcheck_lib.execution import environment_variables
from shellcheck_lib.execution import execution_directory_structure
from shellcheck_lib.util.string import lines_content
from shellcheck_lib_test.default.program_modes import test_case
from shellcheck_lib_test.default.test_resources import assertions
from shellcheck_lib_test.execution.test_execution_directory_structure import \
    is_execution_directory_structure_after_execution
from shellcheck_lib_test.test_resources import value_assertion
from shellcheck_lib_test.test_resources.cli_main_program_via_shell_utils.run import \
    contents_of_file
from shellcheck_lib_test.test_resources.file_checks import FileChecker
from shellcheck_lib_test.test_resources.main_program.main_program_check_base import tests_for_setup_without_preprocessor
from shellcheck_lib_test.test_resources.main_program.main_program_check_for_test_case import SetupWithoutPreprocessor
from shellcheck_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from shellcheck_lib_test.test_resources.process import SubProcessResult, \
    SubProcessResultInfo


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(tests_for_setup_without_preprocessor(OUTPUT_TESTS, main_program_runner))
    ret_val.addTest(test_case.suite_for(main_program_runner))
    return ret_val


class FlagForPrintingAndPreservingSandbox(SetupWithoutPreprocessor):
    def test_case(self) -> str:
        return ''

    def additional_arguments(self) -> list:
        return [OPTION_FOR_KEEPING_SANDBOX_DIRECTORY]

    def expected_result(self) -> value_assertion.ValueAssertion:
        return assertions.assertion_on_process_result(
            value_assertion.And([
                value_assertion.sub_component('exit code',
                                              SubProcessResult.exitcode.fget,
                                              value_assertion.Equals(exit_values.EXECUTION__PASS.exit_code)),
                AssertStdoutIsNameOfExistingSandboxDirectory(),
            ]))


class OutputAndExitCodeFromActPhaseIsEmittedAsResultWhenOptionForExecutingActPhaseIsGiven(SetupWithoutPreprocessor):
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

    def expected_result(self) -> value_assertion.ValueAssertion:
        exit_code = 72
        std_out = 'output to stdout'
        std_err = 'output to stderr\n'
        return assertions.assertion_on_process_result(
            value_assertion.And([
                value_assertion.sub_component('exit code',
                                              SubProcessResult.exitcode.fget,
                                              value_assertion.Equals(exit_code)),
                value_assertion.sub_component('stdout',
                                              SubProcessResult.stdout.fget,
                                              value_assertion.Equals(std_out)),
                value_assertion.sub_component('stderr',
                                              SubProcessResult.stderr.fget,
                                              value_assertion.Equals(std_err)),
            ])
        )


class AssertStdoutIsNameOfExistingSandboxDirectory(value_assertion.ValueAssertion):
    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: value_assertion.MessageBuilder = value_assertion.MessageBuilder()):
        assert isinstance(value, SubProcessResult)
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


class EnvironmentVariablesAreSetCorrectly(SetupWithoutPreprocessor):
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

    def expected_result(self) -> value_assertion.ValueAssertion:
        return value_assertion.And([
            assertions.is_process_result_for_exit_code(exit_values.EXECUTION__PASS.exit_code),
            ExpectedTestEnvironmentVariablesAreSetCorrectlyVa(),
        ])


class ExpectedTestEnvironmentVariablesAreSetCorrectlyVa(value_assertion.ValueAssertion):
    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: value_assertion.MessageBuilder = value_assertion.MessageBuilder()):
        assert isinstance(value, SubProcessResultInfo)
        actual_eds_directory = _get_printed_eds_or_fail(put, value.sub_process_result)
        eds = execution_directory_structure.ExecutionDirectoryStructure(actual_eds_directory)
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


def _get_act_output_to_stdout(eds: execution_directory_structure.ExecutionDirectoryStructure) -> str:
    return contents_of_file(eds.result.stdout_file)


OUTPUT_TESTS = [
    FlagForPrintingAndPreservingSandbox(),
    EnvironmentVariablesAreSetCorrectly(),
    OutputAndExitCodeFromActPhaseIsEmittedAsResultWhenOptionForExecutingActPhaseIsGiven(),
]
