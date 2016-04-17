import pathlib
import shutil
import unittest

from shellcheck_lib.cli.cli_environment.command_line_options import OPTION_FOR_KEEPING_SANDBOX_DIRECTORY, \
    OPTION_FOR_EXECUTING_ACT_PHASE
from shellcheck_lib.execution import environment_variables
from shellcheck_lib.execution import execution_directory_structure
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib.util.string import lines_content
from shellcheck_lib_test.default.program_modes import test_case
from shellcheck_lib_test.execution.test_execution_directory_structure import \
    is_execution_directory_structure_after_execution
from shellcheck_lib_test.test_resources.cli_main_program_via_shell_utils.program_modes.test_case import TestCaseBase, \
    SubProcessResultExpectation, TestCaseFileArgumentArrangement, TestCaseFileArgumentArrangementWithTestActor, \
    ExitCodeAndStdOutputExpectation
from shellcheck_lib_test.test_resources.cli_main_program_via_shell_utils.run import \
    contents_of_file
from shellcheck_lib_test.test_resources.file_checks import FileChecker
from shellcheck_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from shellcheck_lib_test.test_resources.process import SubProcessResult, \
    ExpectedSubProcessResult, SubProcessResultInfo


def expect_pass() -> ExitCodeAndStdOutputExpectation:
    return ExitCodeAndStdOutputExpectation(exit_code=FullResultStatus.PASS.value,
                                           std_out=lines_content([FullResultStatus.PASS.name]))


class TestTestFlagForPrintingAndPreservingSandbox(TestCaseBase):
    def _arrangement(self) -> TestCaseFileArgumentArrangement:
        return TestCaseFileArgumentArrangementWithTestActor(
            test_case_contents='',
            arguments_before_file_argument=(OPTION_FOR_KEEPING_SANDBOX_DIRECTORY,)
        )

    def _expectation(self) -> SubProcessResultExpectation:
        return ExpectSandboxDirectoryIsPrintedAndPreserved()


class ExpectSandboxDirectoryIsPrintedAndPreserved(SubProcessResultExpectation):
    def apply(self, put: unittest.TestCase, actual: SubProcessResultInfo):
        actual_eds_directory = _get_printed_eds_or_fail(put, actual.sub_process_result)
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
        expected = ExpectedSubProcessResult(exitcode=FullResultStatus.PASS.value,
                                            stderr='')
        expected.assert_matches(put, actual.sub_process_result)


class TestEnvironmentVariablesAreSetCorrectly(TestCaseBase):
    def _arrangement(self) -> TestCaseFileArgumentArrangement:
        test_case_source_lines = [
            '[act]',
            'import os',
            _print_variable_name__equals__variable_value(environment_variables.ENV_VAR_HOME),
            _print_variable_name__equals__variable_value(environment_variables.ENV_VAR_ACT),
            _print_variable_name__equals__variable_value(environment_variables.ENV_VAR_TMP),
        ]
        test_case_source = lines_content(test_case_source_lines)
        return TestCaseFileArgumentArrangementWithTestActor(
            test_case_contents=test_case_source,
            arguments_before_file_argument=(OPTION_FOR_KEEPING_SANDBOX_DIRECTORY,)
        )

    def _expectation(self) -> SubProcessResultExpectation:
        return ExpectedTestEnvironmentVariablesAreSetCorrectly()


class ExpectedTestEnvironmentVariablesAreSetCorrectly(SubProcessResultExpectation):
    def apply(self, put: unittest.TestCase, actual: SubProcessResultInfo):
        put.assertEqual(FullResultStatus.PASS.value,
                        actual.sub_process_result.exitcode,
                        'Program is expected to have executed successfully')
        actual_eds_directory = _get_printed_eds_or_fail(put, actual.sub_process_result)
        eds = execution_directory_structure.ExecutionDirectoryStructure(actual_eds_directory)
        actually_printed_variables = _get_act_output_to_stdout(eds).splitlines()
        expected_printed_variables = [
            '%s=%s' % (environment_variables.ENV_VAR_HOME, str(actual.file_argument.parent)),
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


class TestThatOutputAndExitCodeFromActPhaseIsEmittedAsResultWhenOptionForExecutingActPhaseIsGiven(TestCaseBase):
    def _arrangement(self) -> TestCaseFileArgumentArrangement:
        test_case_source = """
[act]
import os
import sys
sys.stdout.write("output to stdout")
sys.stderr.write("output to stderr\\n")
sys.exit(72)
"""
        return TestCaseFileArgumentArrangementWithTestActor(
            test_case_contents=test_case_source,
            arguments_before_file_argument=(OPTION_FOR_EXECUTING_ACT_PHASE,)
        )

    def _expectation(self) -> SubProcessResultExpectation:
        return ExitCodeAndStdOutputExpectation(
            exit_code=72,
            std_out='output to stdout',
            std_err='output to stderr\n',
        )


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.TestSuite([
        TestTestFlagForPrintingAndPreservingSandbox(main_program_runner),
        TestEnvironmentVariablesAreSetCorrectly(main_program_runner),
        TestThatOutputAndExitCodeFromActPhaseIsEmittedAsResultWhenOptionForExecutingActPhaseIsGiven(
            main_program_runner),
    ]))
    ret_val.addTest(test_case.suite_for(main_program_runner))
    return ret_val
