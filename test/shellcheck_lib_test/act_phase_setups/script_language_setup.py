from contextlib import contextmanager
import unittest

from shellcheck_lib.act_phase_setups import script_language_setup as sut
from shellcheck_lib.test_case.sections.act.script_source import ScriptSourceBuilder
from shellcheck_lib.script_language import python3
from shellcheck_lib_test.act_phase_setups.test_resources.act_program_executor import ActProgramExecutorTestSetup, Tests
from shellcheck_lib_test.act_phase_setups.test_resources import py_program


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


class TestSetup(ActProgramExecutorTestSetup):
    def __init__(self):
        self.setup = sut.new_for_script_language_setup(python3.script_language_setup())
        super().__init__(self.setup.executor)

    @contextmanager
    def program_that_copes_stdin_to_stdout(self) -> ScriptSourceBuilder:
        yield self._builder_for(py_program.copy_stdin_to_stdout())

    @contextmanager
    def program_that_prints_to_stderr(self, string_to_print: str) -> ScriptSourceBuilder:
        yield self._builder_for(py_program.write_string_to_stderr(string_to_print))

    @contextmanager
    def program_that_prints_to_stdout(self, string_to_print: str) -> ScriptSourceBuilder:
        yield self._builder_for(py_program.write_string_to_stdout(string_to_print))

    @contextmanager
    def program_that_exits_with_code(self, exit_code: int):
        yield self._builder_for(py_program.exit_with_code(exit_code))

    @contextmanager
    def program_that_prints_cwd_without_new_line_to_stdout(self):
        yield self._builder_for(py_program.write_cwd_to_stdout())

    @contextmanager
    def program_that_prints_value_of_environment_variable_to_stdout(self, var_name: str) -> ScriptSourceBuilder:
        yield self._builder_for(py_program.write_value_of_environment_variable_to_stdout(var_name))

    def _builder_for(self, statements: list) -> ScriptSourceBuilder:
        ret_val = self.setup.script_builder_constructor()
        ret_val.raw_script_statements(statements)
        return ret_val



def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(StandardExecutorTestCases))
    return ret_val


if __name__ == '__main__':
    unittest.main()
