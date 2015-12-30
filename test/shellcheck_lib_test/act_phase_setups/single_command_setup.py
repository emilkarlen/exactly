import os
import pathlib
import sys
import unittest
from contextlib import contextmanager

from shellcheck_lib.act_phase_setups import single_command_setup as sut
from shellcheck_lib.general.std import std_files_dev_null
from shellcheck_lib.test_case.sections.act.phase_setup import SourceSetup
from shellcheck_lib.test_case.sections.act.script_source import ScriptSourceBuilder
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib_test.act_phase_setups.test_resources import py_program
from shellcheck_lib_test.act_phase_setups.test_resources.act_program_executor import ActProgramExecutorTestSetup, Tests
from shellcheck_lib_test.instructions.test_resources.utils import execution_directory_structure
from shellcheck_lib_test.test_resources import python_program_execution as py_exe
from shellcheck_lib_test.test_resources.file_structure import empty_file, File
from shellcheck_lib_test.test_resources.file_structure_utils import tmp_dir_with
from shellcheck_lib_test.test_resources.file_utils import tmp_file_containing_lines


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

    def test_initial_cwd_is_current_dir_and_that_cwd_is_restored_afterwards(self):
        self.tests.test_initial_cwd_is_current_dir_and_that_cwd_is_restored_afterwards()

    def test_environment_variables_are_accessible_by_program(self):
        self.tests.test_environment_variables_are_accessible_by_program()


class ExecutorValidationTestCases(unittest.TestCase):
    def __init__(self, method_name):
        super().__init__(method_name)
        self.setup = sut.act_phase_setup(False)
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
        self.setup = sut.act_phase_setup(False)
        super().__init__(self.setup.executor)

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
        cmd = py_exe.command_line_for_interpreting(src_path)
        ret_val.raw_script_statement(cmd)
        return ret_val


class CommandFileRelativeHomeTestCases(unittest.TestCase):
    def test_validation_fails_when_command_is_relative_but_does_not_exist_relative_home__no_arguments(self):
        setup = sut.act_phase_setup(True)
        source = setup.script_builder_constructor()
        source.raw_script_statement('relative-path-of-non-existing-command')
        actual = setup.executor.validate(pathlib.Path(), source)
        self.assertIs(actual.status,
                      svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      'Validation result')

    def test_validation_succeeds_when_command_is_relative_and_does_exist_relative_home__no_arguments(self):
        setup = sut.act_phase_setup(True)
        source = setup.script_builder_constructor()
        command_file_name = 'command'
        source.raw_script_statement(command_file_name)
        with tmp_dir_with(empty_file(command_file_name)) as home_dir_path:
            actual = setup.executor.validate(home_dir_path, source)
            self.assertIs(actual.status,
                          svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                          'Validation result')

    def test_validation_fails_when_command_is_relative_but_does_not_exist_relative_home__with_arguments(self):
        setup = sut.act_phase_setup(True)
        source = setup.script_builder_constructor()
        source.raw_script_statement('{} {}'.format('non-existing-command', 'argument'))
        actual = setup.executor.validate(pathlib.Path(), source)
        self.assertIs(actual.status,
                      svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      'Validation result')

    def test_validation_succeeds_when_command_is_relative_and_does_exist_relative_home__with_arguments(self):
        setup = sut.act_phase_setup(True)
        source = setup.script_builder_constructor()
        command_file_name = 'command'
        source.raw_script_statement('{} arg1 arg2'.format(command_file_name))
        with tmp_dir_with(empty_file(command_file_name)) as home_dir_path:
            actual = setup.executor.validate(home_dir_path, source)
            self.assertIs(actual.status,
                          svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                          'Validation result')

    def test_validation_succeeds_when_command_is_absolute_without_arguments(self):
        setup = sut.act_phase_setup(True)
        source = setup.script_builder_constructor()
        source.raw_script_statement(py_exe.command_line_for_arguments([]))
        actual = setup.executor.validate(pathlib.Path(), source)
        self.assertIs(actual.status,
                      svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                      'Validation result')

    def test_validation_succeeds_when_command_is_absolute_with_arguments(self):
        setup = sut.act_phase_setup(True)
        source = setup.script_builder_constructor()
        source.raw_script_statement(py_exe.command_line_for_arguments(['argument']))
        actual = setup.executor.validate(pathlib.Path(), source)
        self.assertIs(actual.status,
                      svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                      'Validation result')

    def test_execution_of_command_rel_home__single_argument_that_is_source_file(self):
        exit_code = execute_program_rel_home_that_returns_number_of_arguments(self, '')
        self.assertEqual(0,
                         exit_code)

    def test_execution_of_command_rel_home__multiple_arguments(self):
        exit_code = execute_program_rel_home_that_returns_number_of_arguments(self, '  arg1 arg2')
        num_arguments = 2
        self.assertEqual(num_arguments,
                         exit_code)

    def test_execution_of_command_absolute_path__single_argument_that_is_source_file(self):
        exit_code = execute_absolute_program_that_returns_number_of_arguments(self, [])
        self.assertEqual(0,
                         exit_code)

    def test_execution_of_command_absolute_path__multiple_arguments(self):
        exit_code = execute_absolute_program_that_returns_number_of_arguments(self, ['arg1', 'arg2'])
        num_arguments = 2
        self.assertEqual(num_arguments,
                         exit_code)


def execute_program_rel_home_that_returns_number_of_arguments(puc: unittest.TestCase,
                                                              arguments) -> int:
    setup = sut.act_phase_setup(True)
    source = setup.script_builder_constructor()
    python_interpreter_name = 'python-interpreter'
    command_file_name = 'program.py'
    with tmp_dir_with(File(command_file_name, exit_code_is_number_of_arguments)) as home_dir_path:
        os.symlink(sys.executable, str(home_dir_path / python_interpreter_name), False)
        source.raw_script_statement('{} {}{}'.format(python_interpreter_name,
                                                     home_dir_path / command_file_name,
                                                     arguments))
        actual = setup.executor.validate(home_dir_path, source)
        puc.assertIs(actual.status,
                     svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                     'Validation result')
        with execution_directory_structure() as eds:
            source_setup = SourceSetup(source,
                                       eds.act_dir,
                                       'script-file-stem')
            setup.executor.prepare(source_setup,
                                   home_dir_path,
                                   eds)
            std_files = std_files_dev_null()
            return setup.executor.execute(source_setup,
                                          home_dir_path,
                                          eds,
                                          std_files)


def execute_absolute_program_that_returns_number_of_arguments(puc: unittest.TestCase,
                                                              arguments: list) -> int:
    setup = sut.act_phase_setup(True)
    source = setup.script_builder_constructor()
    command_file_name = 'program.py'
    with tmp_dir_with(File(command_file_name, exit_code_is_number_of_arguments)) as home_dir_path:
        source.raw_script_statement(py_exe.command_line_for_interpreting(home_dir_path / command_file_name,
                                                                         arguments))
        actual = setup.executor.validate(home_dir_path, source)
        puc.assertIs(actual.status,
                     svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                     'Validation result')
        with execution_directory_structure() as eds:
            source_setup = SourceSetup(source,
                                       eds.act_dir,
                                       'script-file-stem')
            setup.executor.prepare(source_setup,
                                   home_dir_path,
                                   eds)
            std_files = std_files_dev_null()
            return setup.executor.execute(source_setup,
                                          home_dir_path,
                                          eds,
                                          std_files)


exit_code_is_number_of_arguments = """
import sys
sys.exit(len(sys.argv) - 1)
"""


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(ExecutorValidationTestCases))
    ret_val.addTest(unittest.makeSuite(StandardExecutorTestCases))
    ret_val.addTest(unittest.makeSuite(CommandFileRelativeHomeTestCases))
    return ret_val


if __name__ == '__main__':
    unittest.main()
