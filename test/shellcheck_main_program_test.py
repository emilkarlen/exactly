import pathlib
import shutil
import unittest
import sys

from shellcheck_lib.cli.main_program import EXIT_INVALID_USAGE
import shellcheck_lib.cli.utils
from shellcheck_lib.execution import execution_directory_structure
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib.test_case import instructions
from shellcheck_lib_test.execution.test_execution_directory_structure import \
    is_execution_directory_structure_after_execution
from shellcheck_lib_test.util.file_checks import FileChecker
from shellcheck_lib_test.util.with_tmp_file import lines_content, SubProcessResult, \
    ExpectedSubProcessResult, run_subprocess_with_file_arg__full, SubProcessResultInfo

SRC_DIR_NAME = 'src'
MAIN_PROGRAM_FILE_NAME = 'shellcheck.py'


def shellcheck_src_path(dir_of_this_file: pathlib.Path) -> pathlib.Path:
    return dir_of_this_file.parent / SRC_DIR_NAME / MAIN_PROGRAM_FILE_NAME


class UnitTestCaseWithUtils(unittest.TestCase):
    def _run_shellcheck_in_sub_process(self,
                                       test_case_source: str,
                                       flags: list=()) -> SubProcessResultInfo:
        return run_shellcheck_in_sub_process(self,
                                             test_case_source=test_case_source,
                                             flags=flags)


class TestsInvokation(UnitTestCaseWithUtils):
    def test_exit_status_with_invalid_invokation_for_test_case(self):
        # ARRANGE #
        test_case_source = ''
        # ACT #
        actual = self._run_shellcheck_in_sub_process(test_case_source,
                                                     flags=['--illegal-flag-42847920189']).sub_process_result
        # ASSERT #
        self.assertEqual(EXIT_INVALID_USAGE,
                         actual.exitcode,
                         'Expected exit code for invalid invokation')
        self.assertEqual('',
                         actual.stdout,
                         'Expects no output on stdout for invalid invokation')

    def test_exit_status_with_invalid_invokation_for_test_suite(self):
        # ARRANGE #
        test_suite_source = ''
        # ACT #
        actual = self._run_shellcheck_in_sub_process(test_suite_source,
                                                     flags=['suite', '--illegal-flag-42847920189']).sub_process_result
        # ASSERT #
        self.assertEqual(EXIT_INVALID_USAGE,
                         actual.exitcode,
                         'Expected exit code for invalid invokation')
        self.assertEqual('',
                         actual.stdout,
                         'Expects no output on stdout for invalid invokation')


class BasicTestsWithNoCliFlags(UnitTestCaseWithUtils):
    def test_empty_test_case(self):
        # ARRANGE #
        test_case_source = ''
        # ACT #
        actual = self._run_shellcheck_in_sub_process(test_case_source).sub_process_result
        # ASSERT #
        SUCCESSFUL_RESULT.assert_matches(self,
                                         actual)

    def test_test_case_with_only_phase_headers(self):
        # ARRANGE #
        test_case_source_lines = [
            '[setup]',
            '[act]',
            '[assert]',
            '[cleanup]',
        ]
        test_case_source = lines_content(test_case_source_lines)
        # ACT #
        actual = self._run_shellcheck_in_sub_process(test_case_source).sub_process_result
        # ASSERT #
        SUCCESSFUL_RESULT.assert_matches(self,
                                         actual)


class TestsWithPreservedExecutionDirectoryStructure(UnitTestCaseWithUtils):
    def test_flag_for_printing_and_preserving_eds(self):
        # ARRANGE #
        test_case_source = ''
        # ACT #
        actual = self._run_shellcheck_in_sub_process(test_case_source,
                                                     flags=['--keep']).sub_process_result
        # ASSERT #
        actual_eds_directory = self._get_printed_eds_or_fail(actual)
        actual_eds_path = pathlib.Path(actual_eds_directory)
        if actual_eds_path.exists():
            if actual_eds_path.is_dir():
                is_execution_directory_structure_after_execution(
                    FileChecker(self, 'Not an Execution Directory Structure'),
                    actual_eds_directory)
                self._remove_if_is_directory(actual_eds_directory)
            else:
                self.fail('Output from program is not the EDS (not a directory): "%s"' % actual_eds_directory)
        else:
            self.fail('The output from the program is not the EDS: "%s"' % actual_eds_directory)
        expected = ExpectedSubProcessResult(exitcode=FullResultStatus.PASS.value,
                                            stderr='')
        expected.assert_matches(self,
                                actual)

    def test_environment_variables(self):
        # ARRANGE #
        test_case_source_lines = [
            '[act]',
            'import os',
            self._print_variable_name__equals__variable_value(instructions.ENV_VAR_HOME),
            self._print_variable_name__equals__variable_value(instructions.ENV_VAR_TEST),
            self._print_variable_name__equals__variable_value(instructions.ENV_VAR_TMP),
        ]
        test_case_source = lines_content(test_case_source_lines)
        # ACT #
        actual = self._run_shellcheck_in_sub_process(test_case_source,
                                                     flags=['--interpreter',
                                                            shellcheck_lib.cli.utils.INTERPRETER_FOR_TEST,
                                                            '--keep'])
        # ASSERT #
        self.assertEqual(FullResultStatus.PASS.value,
                         actual.sub_process_result.exitcode,
                         'Program is expected to have executed successfully')
        actual_eds_directory = self._get_printed_eds_or_fail(actual.sub_process_result)
        eds = execution_directory_structure.ExecutionDirectoryStructure(actual_eds_directory)
        actually_printed_variables = self._get_act_output_to_stdout(eds).splitlines()
        expected_printed_variables = [
            '%s=%s' % (instructions.ENV_VAR_HOME, str(actual.file_argument.parent)),
            '%s=%s' % (instructions.ENV_VAR_TEST, str(eds.test_root_dir)),
            '%s=%s' % (instructions.ENV_VAR_TMP, str(eds.tmp_dir)),
        ]
        self.assertEqual(expected_printed_variables,
                         actually_printed_variables,
                         'Environment variables printed by the act script')
        self._remove_if_is_directory(actual_eds_directory)

    def _remove_if_is_directory(self, actual_eds_directory: str):
        actual_eds_path = pathlib.Path(actual_eds_directory)
        if actual_eds_path.is_dir():
            shutil.rmtree(actual_eds_directory)

    def _get_printed_eds_or_fail(self, actual: SubProcessResult) -> str:
        printed_lines = actual.stdout.splitlines()
        self.assertEqual(1,
                         len(printed_lines),
                         'Number of printed printed lines should be exactly 1')
        actual_eds_directory = printed_lines[0]
        return actual_eds_directory

    @staticmethod
    def _print_variable_name__equals__variable_value(variable_name: str) -> str:
        return 'print("%s=" + os.environ["%s"])' % (variable_name, variable_name)

    def _get_act_output_to_stdout(self,
                                  eds: execution_directory_structure.ExecutionDirectoryStructure) -> str:
        return _contents_of_file(eds.result.std.stdout_file)


class TestsExecuteActPhase(UnitTestCaseWithUtils):
    def test_that_output_and_exit_code_from_act_phase_is_emitted_as_result_of_shellcheck(self):
        # ARRANGE #
        test_case_source_lines = [
            '[act]',
            'import os',
            'import sys',
            'sys.stdout.write("output to stdout")',
            'sys.stderr.write("output to stderr\\n")',
            'sys.exit(72)',
        ]
        test_case_source = lines_content(test_case_source_lines)
        # ACT #
        actual = self._run_shellcheck_in_sub_process(test_case_source,
                                                     flags=['--interpreter',
                                                            shellcheck_lib.cli.utils.INTERPRETER_FOR_TEST,
                                                            '--act']).sub_process_result
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


SUCCESSFUL_RESULT = ExpectedSubProcessResult(exitcode=FullResultStatus.PASS.value,
                                             stdout=lines_content([FullResultStatus.PASS.name]),
                                             stderr='')


def run_shellcheck_in_sub_process(puc: unittest.TestCase,
                                  test_case_source: str,
                                  flags: list=()) -> SubProcessResultInfo:
    cwd = pathlib.Path.cwd()
    # print('# DEBUG: cwd: ' + str(cwd))
    if not sys.executable:
        puc.fail('Cannot execute test since the name of the Python 3 interpreter is not found in sys.executable.')
    shellcheck_path = shellcheck_src_path(cwd)
    args_without_file = [sys.executable, str(shellcheck_path)] + list(flags)
    return run_subprocess_with_file_arg__full(args_without_file, test_case_source)


def _contents_of_file(path: pathlib.Path) -> str:
    with path.open() as f:
        return f.read()


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestsInvokation))
    ret_val.addTest(unittest.makeSuite(BasicTestsWithNoCliFlags))
    ret_val.addTest(unittest.makeSuite(TestsWithPreservedExecutionDirectoryStructure))
    ret_val.addTest(unittest.makeSuite(TestsExecuteActPhase))
    return ret_val


if __name__ == '__main__':
    unittest.main()
