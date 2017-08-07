import pathlib
import shutil
import unittest

from exactly_lib.cli import main_program
from exactly_lib.cli.cli_environment.program_modes.test_case.command_line_options import \
    OPTION_FOR_EXECUTING_ACT_PHASE, OPTION_FOR_KEEPING_SANDBOX_DIRECTORY
from exactly_lib.execution import environment_variables, exit_values
from exactly_lib.section_document.syntax import section_header
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case_file_structure import sandbox_directory_structure
from exactly_lib.util.string import lines_content
from exactly_lib_test.default.test_resources.internal_main_program_runner import \
    main_program_runner_with_default_setup_in_same_process
from exactly_lib_test.default.test_resources.test_case_file_elements import phase_header_line
from exactly_lib_test.test_case_file_structure.sandbox_directory_structure import \
    is_sandbox_directory_structure_after_execution
from exactly_lib_test.test_resources.assertions.file_checks import FileChecker
from exactly_lib_test.test_resources.cli_main_program_via_sub_process_utils.run import \
    contents_of_file
from exactly_lib_test.test_resources.main_program.main_program_check_base import tests_for_setup_without_preprocessor
from exactly_lib_test.test_resources.main_program.main_program_check_for_test_case import \
    SetupWithoutPreprocessorAndTestActor
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.process import SubProcessResult, \
    SubProcessResultInfo
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt, process_result_info_assertions
from exactly_lib_test.test_resources.value_assertions.process_result_info_assertions import \
    process_result_for_exit_value, \
    is_process_result_for_exit_code


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(tests_for_setup_without_preprocessor(MISC_TESTS, main_program_runner))
    ret_val.addTest(tests_for_setup_without_preprocessor(SPECIAL_EXECUTION_CONFIGURATIONS_TESTS, main_program_runner))
    return ret_val


def suite() -> unittest.TestSuite:
    return suite_for(main_program_runner_with_default_setup_in_same_process())


class InvalidCommandLineOptionShouldExitWithInvalidUsageStatus(SetupWithoutPreprocessorAndTestActor):
    def additional_arguments(self) -> list:
        return ['--invalid-option-that-should-cause-failure']

    def expected_result(self) -> asrt.ValueAssertion:
        return is_process_result_for_exit_code(main_program.EXIT_INVALID_USAGE)

    def test_case(self) -> str:
        return ''


class EmptyTestCaseShouldPass(SetupWithoutPreprocessorAndTestActor):
    def expected_result(self) -> asrt.ValueAssertion:
        return process_result_for_exit_value(exit_values.EXECUTION__PASS)

    def test_case(self) -> str:
        return ''


class AllPhasesEmptyShouldPass(SetupWithoutPreprocessorAndTestActor):
    def test_case(self) -> str:
        test_case_lines = [phase_header_line(phase)
                           for phase in phase_identifier.ALL]
        return lines_content(test_case_lines)

    def expected_result(self) -> asrt.ValueAssertion:
        return process_result_for_exit_value(exit_values.EXECUTION__PASS)


class WhenAPhaseHasInvalidPhaseNameThenExitStatusShouldIndicateThis(SetupWithoutPreprocessorAndTestActor):
    def test_case(self) -> str:
        test_case_lines = [
            section_header('invalid phase name'),
        ]
        return lines_content(test_case_lines)

    def expected_result(self) -> asrt.ValueAssertion:
        return process_result_for_exit_value(exit_values.NO_EXECUTION__SYNTAX_ERROR)


class FlagForPrintingAndPreservingSandbox(SetupWithoutPreprocessorAndTestActor):
    def test_case(self) -> str:
        return ''

    def additional_arguments(self) -> list:
        return [OPTION_FOR_KEEPING_SANDBOX_DIRECTORY]

    def expected_result(self) -> asrt.ValueAssertion:
        return process_result_info_assertions.assertion_on_process_result(
            asrt.And([
                asrt.sub_component('exit code',
                                   SubProcessResult.exitcode.fget,
                                   asrt.Equals(exit_values.EXECUTION__PASS.exit_code)),
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

    def expected_result(self) -> asrt.ValueAssertion:
        exit_code = 72
        std_out = 'output to stdout'
        std_err = 'output to stderr\n'
        return process_result_info_assertions.assertion_on_process_result(
            asrt.And([
                asrt.sub_component('exit code',
                                   SubProcessResult.exitcode.fget,
                                   asrt.Equals(exit_code)),
                asrt.sub_component('stdout',
                                   SubProcessResult.stdout.fget,
                                   asrt.Equals(std_out)),
                asrt.sub_component('stderr',
                                   SubProcessResult.stderr.fget,
                                   asrt.Equals(std_err)),
            ])
        )


class AssertStdoutIsNameOfExistingSandboxDirectory(asrt.ValueAssertion):
    def apply(self,
              put: unittest.TestCase,
              value: SubProcessResult,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        actual_sds_directory = _get_printed_sds_or_fail(put, value)
        actual_sds_path = pathlib.Path(actual_sds_directory)
        if actual_sds_path.exists():
            if actual_sds_path.is_dir():
                is_sandbox_directory_structure_after_execution(
                    FileChecker(put, 'Not an sandbox directory structure'),
                    actual_sds_directory)
                _remove_if_is_directory(actual_sds_directory)
            else:
                put.fail('Output from program is not the sandbox (not a directory): "%s"' % actual_sds_directory)
        else:
            put.fail('The output from the program is not the sandbox: "%s"' % actual_sds_directory)


class EnvironmentVariablesAreSetCorrectly(SetupWithoutPreprocessorAndTestActor):
    def additional_arguments(self) -> list:
        return [OPTION_FOR_KEEPING_SANDBOX_DIRECTORY]

    def test_case(self) -> str:
        test_case_source_lines = [
            '[act]',
            'import os',
            _print_variable_name__equals__variable_value(environment_variables.ENV_VAR_HOME_CASE),
            _print_variable_name__equals__variable_value(environment_variables.ENV_VAR_ACT),
            _print_variable_name__equals__variable_value(environment_variables.ENV_VAR_TMP),
        ]
        return lines_content(test_case_source_lines)

    def expected_result(self) -> asrt.ValueAssertion:
        return asrt.And([
            process_result_info_assertions.is_process_result_for_exit_code(exit_values.EXECUTION__PASS.exit_code),
            ExpectedTestEnvironmentVariablesAreSetCorrectlyVa(),
        ])


class ExpectedTestEnvironmentVariablesAreSetCorrectlyVa(asrt.ValueAssertion):
    def apply(self,
              put: unittest.TestCase,
              value: SubProcessResultInfo,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        actual_sds_directory = _get_printed_sds_or_fail(put, value.sub_process_result)
        sds = sandbox_directory_structure.SandboxDirectoryStructure(actual_sds_directory)
        actually_printed_variables = _get_act_output_to_stdout(sds).splitlines()
        expected_printed_variables = [
            '%s=%s' % (environment_variables.ENV_VAR_HOME_CASE, str(value.file_argument.parent)),
            '%s=%s' % (environment_variables.ENV_VAR_ACT, str(sds.act_dir)),
            '%s=%s' % (environment_variables.ENV_VAR_TMP, str(sds.tmp.user_dir)),
        ]
        put.assertEqual(expected_printed_variables,
                        actually_printed_variables,
                        'Environment variables printed by the act script')
        _remove_if_is_directory(actual_sds_directory)


def _remove_if_is_directory(actual_sds_directory: str):
    actual_sds_path = pathlib.Path(actual_sds_directory)
    if actual_sds_path.is_dir():
        shutil.rmtree(actual_sds_directory)


def _get_printed_sds_or_fail(put: unittest.TestCase, actual: SubProcessResult) -> str:
    printed_lines = actual.stdout.splitlines()
    put.assertEqual(1,
                    len(printed_lines),
                    'Number of printed printed lines should be exactly 1')
    actual_sds_directory = printed_lines[0]
    return actual_sds_directory


def _print_variable_name__equals__variable_value(variable_name: str) -> str:
    return 'print("%s=" + os.environ["%s"])' % (variable_name, variable_name)


def _get_act_output_to_stdout(sds: sandbox_directory_structure.SandboxDirectoryStructure) -> str:
    return contents_of_file(sds.result.stdout_file)


SPECIAL_EXECUTION_CONFIGURATIONS_TESTS = [
    FlagForPrintingAndPreservingSandbox(),
    OutputAndExitCodeFromActPhaseIsEmittedAsResultWhenOptionForExecutingActPhaseIsGiven(),
]

MISC_TESTS = [
    InvalidCommandLineOptionShouldExitWithInvalidUsageStatus(),
    WhenAPhaseHasInvalidPhaseNameThenExitStatusShouldIndicateThis(),
    EnvironmentVariablesAreSetCorrectly(),
]

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
