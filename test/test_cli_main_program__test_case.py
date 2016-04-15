import pathlib
import shutil
import unittest

from shellcheck_lib.cli.cli_environment.command_line_options import OPTION_FOR_KEEPING_SANDBOX_DIRECTORY
from shellcheck_lib.execution import environment_variables
from shellcheck_lib.execution import execution_directory_structure
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib.util.string import lines_content
from shellcheck_lib_test.cli.test_resources.execute_main_program import arguments_for_test_interpreter_and_more_tuple
from shellcheck_lib_test.default.test_resources import default_main_program_case_preprocessing
from shellcheck_lib_test.execution.test_execution_directory_structure import \
    is_execution_directory_structure_after_execution
from shellcheck_lib_test.test_resources.cli_main_program_via_shell_utils.program_modes.test_case import TestCaseBase, \
    SubProcessResultExpectation, TestCaseFileArgumentArrangement, TestCaseFileArgumentArrangementWithTestActor, \
    ExitCodeAndStdOutExpectation
from shellcheck_lib_test.test_resources.cli_main_program_via_shell_utils.run import \
    run_shellcheck_in_sub_process_with_file_argument, \
    contents_of_file
from shellcheck_lib_test.test_resources.file_checks import FileChecker
from shellcheck_lib_test.test_resources.main_program import main_program_check_for_test_case
from shellcheck_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from shellcheck_lib_test.test_resources.process import SubProcessResult, \
    ExpectedSubProcessResult, SubProcessResultInfo


class UnitTestCaseWithUtils(unittest.TestCase):
    def _run_shellcheck_in_sub_process(self,
                                       test_case_source: str,
                                       flags: tuple = ()) -> SubProcessResultInfo:
        return run_shellcheck_in_sub_process_with_file_argument(self,
                                                                file_contents=test_case_source,
                                                                flags=flags)

    def _run_shellcheck_with_test_interpreter_in_sub_process(
            self,
            test_case_source: str,
            flags_before_interpreter_arg: tuple = ()) -> SubProcessResultInfo:
        flags = arguments_for_test_interpreter_and_more_tuple(flags_before_interpreter_arg)
        return run_shellcheck_in_sub_process_with_file_argument(self,
                                                                file_contents=test_case_source,
                                                                flags=flags)


def expect_pass() -> ExitCodeAndStdOutExpectation:
    return ExitCodeAndStdOutExpectation(exit_code=FullResultStatus.PASS.value,
                                        std_out=lines_content([FullResultStatus.PASS.name]))


class TestNoCliFlagsANDEmptyTestCase(TestCaseBase):
    def _arrangement(self) -> TestCaseFileArgumentArrangement:
        return TestCaseFileArgumentArrangementWithTestActor(
            test_case_contents=''
        )

    def _expectation(self) -> SubProcessResultExpectation:
        return expect_pass()


class TestNoCliFlagsANDTestCaseWithOnlyPhaseHeaders(TestCaseBase):
    def _arrangement(self) -> TestCaseFileArgumentArrangement:
        return TestCaseFileArgumentArrangementWithTestActor(
            test_case_contents=lines_content([
                '[conf]',
                '[setup]',
                '[act]',
                '[before-assert]',
                '[assert]',
                '[cleanup]',
            ])
        )

    def _expectation(self) -> SubProcessResultExpectation:
        return expect_pass()


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


class TestsExecuteActPhase(UnitTestCaseWithUtils):
    def test_that_output_and_exit_code_from_act_phase_is_emitted_as_result_of_shellcheck(self):
        # ARRANGE #
        test_case_source = """
[act]
import os
import sys
sys.stdout.write("output to stdout")
sys.stderr.write("output to stderr\\n")
sys.exit(72)
"""
        # ACT #
        actual = self._run_shellcheck_in_sub_process(
            test_case_source,
            flags=arguments_for_test_interpreter_and_more_tuple(['--act'])).sub_process_result
        # ASSERT #
        self.assertEqual(72,
                         actual.exitcode,
                         'Program is expected to exit with same exit code as act script')
        self.assertEqual('output to stdout',
                         actual.stdout,
                         'Output on stdout is expected to be same as that of act script')
        self.assertEqual('output to stderr\n',
                         actual.stderr,
                         'Output on stderr is expected to be same as that of act script')


class TestTestCasePreprocessing(
    main_program_check_for_test_case.TestsForSetupWithPreprocessorExternally):
    def test_transformation_into_test_case_that_pass(self):
        self._check([],
                    default_main_program_case_preprocessing.TransformationIntoTestCaseThatPass())

    def test_transformation_into_test_case_that_parser_error(self):
        self._check([],
                    default_main_program_case_preprocessing.TransformationIntoTestCaseThatParserError())


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestsExecuteActPhase))
    ret_val.addTest(unittest.makeSuite(TestTestCasePreprocessing))
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.TestSuite([
        TestNoCliFlagsANDEmptyTestCase(main_program_runner),
        TestNoCliFlagsANDTestCaseWithOnlyPhaseHeaders(main_program_runner),
        TestTestFlagForPrintingAndPreservingSandbox(main_program_runner),
        TestEnvironmentVariablesAreSetCorrectly(main_program_runner),
    ]))
    return ret_val
