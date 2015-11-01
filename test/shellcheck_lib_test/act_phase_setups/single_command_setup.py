from contextlib import contextmanager
import pathlib
import unittest
import sys

from shellcheck_lib.act_phase_setups import single_command_setup as sut
from shellcheck_lib.test_case.sections.act.script_source import ScriptSourceBuilder
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib_test.act_phase_setups.test_resources.act_program_executor import ActProgramExecutorTestSetup, Tests
from shellcheck_lib_test.act_phase_setups.test_resources import py_program
from shellcheck_lib_test.util.with_tmp_file import tmp_file_containing_lines


class StandardExecutorTestCases(unittest.TestCase):
    def __init__(self, method_name):
        super().__init__(method_name)
        self.tests = Tests(self, TestSetup())

    def test_stdout_is_connected_to_program(self):
        self.tests.test_stdout_is_connected_to_program()

    def test_stderr_is_connected_to_program(self):
        self.tests.test_stderr_is_connected_to_program()

    def test_stdin_and_stdout_are_connected_to_program(self):
        self.tests.test_stdin_and_stdout_are_connected_to_program()

    def test_exit_code_is_returned(self):
        self.tests.test_exit_code_is_returned()

    def test_initial_cwd_is_act_directory_and_that_cwd_is_restored_afterwards(self):
        self.tests.test_initial_cwd_is_act_directory_and_that_cwd_is_restored_afterwards()

    def test_environment_variables_are_accessible_by_program(self):
        self.tests.test_environment_variables_are_accessible_by_program()


class ExecutorValidationTestCases(unittest.TestCase):
    def __init__(self, method_name):
        super().__init__(method_name)
        self.setup = sut.act_phase_setup()
        self.home_dir_as_current_dir = pathlib.Path()

    def test_validation_fails_when_there_are_no_statements(self):
        source = self._empty_builder()
        actual = self.setup.executor.validate(self.home_dir_as_current_dir, source)
        self.assertIs(actual.status,
                      svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      'Validation result')

    def test_validation_fails_when_there_are_more_than_one_statements(self):
        source = self._empty_builder()
        source.raw_script_statement('statement 1')
        source.raw_script_statement('statement 2')
        actual = self.setup.executor.validate(self.home_dir_as_current_dir, source)
        self.assertIs(actual.status,
                      svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      'Validation result')

    def test_validation_succeeds_when_there_is_exactly_one_statements(self):
        source = self._empty_builder()
        source.raw_script_statement('statement 1')
        actual = self.setup.executor.validate(self.home_dir_as_current_dir, source)
        self.assertIs(actual.status,
                      svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                      'Validation result')

    def test_validation_fails_when_there_is_a_single_statement_line_but_this_line_is_only_space(self):
        source = self._empty_builder()
        source.raw_script_statement('  \t')
        actual = self.setup.executor.validate(self.home_dir_as_current_dir, source)
        self.assertIs(actual.status,
                      svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      'Validation result')

    def test_that_comment_lines_are_ignored(self):
        source = self._empty_builder()
        source.raw_script_statement('statement 1')
        source.comment_line('comment 1')
        actual = self.setup.executor.validate(self.home_dir_as_current_dir, source)
        self.assertIs(actual.status,
                      svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                      'Validation result')

    def _empty_builder(self) -> ScriptSourceBuilder:
        return self.setup.script_builder_constructor()


class TestSetup(ActProgramExecutorTestSetup):
    def __init__(self):
        self.setup = sut.act_phase_setup()
        super().__init__(self.setup.executor)
        self.python_executable = sys.executable

    @contextmanager
    def program_that_copes_stdin_to_stdout(self) -> ScriptSourceBuilder:
        return self._builder_for_executing_source_from_py_file(py_program.copy_stdin_to_stdout())

    @contextmanager
    def program_that_prints_to_stderr(self, string_to_print: str) -> ScriptSourceBuilder:
        return self._builder_for_executing_source_from_py_file(py_program.write_string_to_stderr(string_to_print))

    @contextmanager
    def program_that_prints_to_stdout(self, string_to_print: str) -> ScriptSourceBuilder:
        return self._builder_for_executing_source_from_py_file(py_program.write_string_to_stdout(string_to_print))

    @contextmanager
    def program_that_exits_with_code(self, exit_code: int):
        return self._builder_for_executing_source_from_py_file(py_program.exit_with_code(exit_code))

    @contextmanager
    def program_that_prints_cwd_without_new_line_to_stdout(self):
        return self._builder_for_executing_source_from_py_file(py_program.write_cwd_to_stdout())

    @contextmanager
    def program_that_prints_value_of_environment_variable_to_stdout(self, var_name: str) -> ScriptSourceBuilder:
        return self._builder_for_executing_source_from_py_file(
            py_program.write_value_of_environment_variable_to_stdout(var_name))

    def _builder_for_executing_source_from_py_file(self, statements: list) -> ScriptSourceBuilder:
        with tmp_file_containing_lines(statements) as src_path:
            yield self._builder_for_executing_py_file(src_path)

    def _builder_for_executing_py_file(self, src_path: pathlib.Path) -> ScriptSourceBuilder:
        ret_val = self.setup.script_builder_constructor()
        cmd = self.python_executable + ' ' + str(src_path)
        ret_val.raw_script_statement(cmd)
        return ret_val


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(ExecutorValidationTestCases))
    ret_val.addTest(unittest.makeSuite(StandardExecutorTestCases))
    return ret_val


if __name__ == '__main__':
    unittest.main()
