import os
import pathlib
import sys
import unittest
from contextlib import contextmanager

from exactly_lib.act_phase_setups import single_command_setup as sut
from exactly_lib.execution.act_phase import SourceSetup
from exactly_lib.test_case.phases.act.program_source import ActSourceBuilder, ActSourceBuilderForStatementLines
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.std import std_files_dev_null
from exactly_lib_test.act_phase_setups.test_resources import py_program
from exactly_lib_test.act_phase_setups.test_resources.act_program_executor import Configuration, \
    suite_for_execution, run_execute
from exactly_lib_test.test_resources import python_program_execution as py_exe
from exactly_lib_test.test_resources.execution.utils import execution_directory_structure
from exactly_lib_test.test_resources.file_structure import File
from exactly_lib_test.test_resources.file_structure_utils import tmp_dir_with
from exactly_lib_test.test_resources.file_utils import tmp_file_containing_lines


class TestValidation(unittest.TestCase):
    def __init__(self, method_name):
        super().__init__(method_name)
        self.setup = sut.act_phase_setup()
        self.home_dir_as_current_dir = pathlib.Path()

    def test_fails_when_there_are_no_statements(self):
        source = self._empty_builder()
        actual = self.setup.executor.validate(self.home_dir_as_current_dir, source)
        self.assertIs(actual.status,
                      svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      'Validation result')

    def test_fails_when_there_are_more_than_one_statements(self):
        source = self._empty_builder()
        source.raw_script_statement('statement 1')
        source.raw_script_statement('statement 2')
        actual = self.setup.executor.validate(self.home_dir_as_current_dir, source)
        self.assertIs(actual.status,
                      svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      'Validation result')

    def test_succeeds_when_there_is_exactly_one_statements(self):
        source = self._empty_builder()
        source.raw_script_statement('statement 1')
        actual = self.setup.executor.validate(self.home_dir_as_current_dir, source)
        self.assertIs(actual.status,
                      svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                      'Validation result')

    def test_fails_when_there_is_a_single_statement_line_but_this_line_is_only_space(self):
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

    def _empty_builder(self) -> ActSourceBuilder:
        return self.setup.script_builder_constructor()


class TheConfiguration(Configuration):
    def __init__(self):
        self.setup = sut.act_phase_setup()
        super().__init__(self.setup.executor)

    @contextmanager
    def program_that_copes_stdin_to_stdout(self) -> ActSourceBuilder:
        return self._builder_for_executing_source_from_py_file(py_program.copy_stdin_to_stdout())

    @contextmanager
    def program_that_prints_to_stderr(self, string_to_print: str) -> ActSourceBuilder:
        return self._builder_for_executing_source_from_py_file(py_program.write_string_to_stderr(string_to_print))

    @contextmanager
    def program_that_prints_to_stdout(self, string_to_print: str) -> ActSourceBuilder:
        return self._builder_for_executing_source_from_py_file(py_program.write_string_to_stdout(string_to_print))

    @contextmanager
    def program_that_exits_with_code(self, exit_code: int):
        return self._builder_for_executing_source_from_py_file(py_program.exit_with_code(exit_code))

    @contextmanager
    def program_that_prints_cwd_without_new_line_to_stdout(self):
        return self._builder_for_executing_source_from_py_file(py_program.write_cwd_to_stdout())

    @contextmanager
    def program_that_prints_value_of_environment_variable_to_stdout(self, var_name: str) -> ActSourceBuilder:
        return self._builder_for_executing_source_from_py_file(
            py_program.write_value_of_environment_variable_to_stdout(var_name))

    def _builder_for_executing_source_from_py_file(self, statements: list) -> ActSourceBuilder:
        with tmp_file_containing_lines(statements) as src_path:
            yield self._builder_for_executing_py_file(src_path)

    def _builder_for_executing_py_file(self, src_path: pathlib.Path) -> ActSourceBuilder:
        ret_val = self.setup.script_builder_constructor()
        cmd = py_exe.command_line_for_interpreting(src_path)
        ret_val.raw_script_statement(cmd)
        return ret_val


class TestWhenInterpreterDoesNotExistThanTheResultShouldBeHardError(unittest.TestCase):
    def runTest(self):
        executor = sut.ActSourceExecutorForSingleCommand()
        source = self._source_that_references_non_existing_program()
        exit_code_or_hard_error = run_execute(self,
                                              executor,
                                              source)
        self.assertTrue(exit_code_or_hard_error.is_hard_error,
                        'Expecting a HARD ERROR')

    def _source_that_references_non_existing_program(self) -> ActSourceBuilderForStatementLines:
        source = ActSourceBuilderForStatementLines()
        interpreter_path = pathlib.Path().cwd().resolve() / 'non-existing-interpreter'
        source.raw_script_statement(str(interpreter_path))
        return source


def execute_program_rel_home_that_returns_number_of_arguments(puc: unittest.TestCase,
                                                              arguments) -> int:
    setup = sut.act_phase_setup()
    source = setup.script_builder_constructor()
    executor = setup.executor
    python_interpreter_name = 'python-interpreter'
    command_file_name = 'program.py'
    with tmp_dir_with(File(command_file_name, exit_code_is_number_of_arguments)) as home_dir_path:
        os.symlink(sys.executable, str(home_dir_path / python_interpreter_name), False)
        source.raw_script_statement('{} {}{}'.format(python_interpreter_name,
                                                     home_dir_path / command_file_name,
                                                     arguments))
        actual = executor.validate(home_dir_path, source)
        puc.assertIs(actual.status,
                     svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                     'Validation result')
        with execution_directory_structure() as eds:
            source_setup = SourceSetup(source,
                                       eds.act_dir,
                                       'script-file-stem')
            executor.prepare(source_setup,
                             home_dir_path,
                             eds)
            std_files = std_files_dev_null()
            return executor.execute(source_setup,
                                    home_dir_path,
                                    eds,
                                    std_files)


def execute_absolute_program_that_returns_number_of_arguments(puc: unittest.TestCase,
                                                              arguments: list) -> int:
    setup = sut.act_phase_setup()
    source = setup.script_builder_constructor()
    executor = setup.executor
    command_file_name = 'program.py'
    with tmp_dir_with(File(command_file_name, exit_code_is_number_of_arguments)) as home_dir_path:
        source.raw_script_statement(py_exe.command_line_for_interpreting(home_dir_path / command_file_name,
                                                                         arguments))
        actual = executor.validate(home_dir_path, source)
        puc.assertIs(actual.status,
                     svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                     'Validation result')
        with execution_directory_structure() as eds:
            source_setup = SourceSetup(source,
                                       eds.act_dir,
                                       'script-file-stem')
            executor.prepare(source_setup,
                             home_dir_path,
                             eds)
            std_files = std_files_dev_null()
            return executor.execute(source_setup,
                                    home_dir_path,
                                    eds,
                                    std_files)


exit_code_is_number_of_arguments = """
import sys
sys.exit(len(sys.argv) - 1)
"""


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestValidation))
    ret_val.addTest(unittest.makeSuite(TestWhenInterpreterDoesNotExistThanTheResultShouldBeHardError))
    ret_val.addTest(suite_for_execution(TheConfiguration()))
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
