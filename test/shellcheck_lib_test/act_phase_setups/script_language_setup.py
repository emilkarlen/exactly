from contextlib import contextmanager
import unittest

from shellcheck_lib.act_phase_setups import script_language_setup as sut
from shellcheck_lib.test_case.sections.act.script_source import ScriptSourceBuilder
from shellcheck_lib.script_language import python3
from shellcheck_lib_test.test_case.test_resources.act_program_executor import ActProgramExecutorTestSetup, Tests


class TestCases(unittest.TestCase):
    def __init__(self, method_name='runTest'):
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
        self.language = python3.language()
        self.language_setup = python3.script_language_setup()
        super().__init__(sut.ActProgramExecutorForScriptLanguage(self.language_setup))

    @contextmanager
    def program_that_copes_stdin_to_stdout(self) -> ScriptSourceBuilder:
        ret_val = ScriptSourceBuilder(self.language)
        ret_val.raw_script_statements([
            'import sys',
            "sys.stdout.write(sys.stdin.read())"
        ])
        yield ret_val

    @contextmanager
    def program_that_prints_to_stderr(self, string_to_print: str) -> ScriptSourceBuilder:
        ret_val = ScriptSourceBuilder(self.language)
        ret_val.raw_script_statements([
            'import sys',
            "sys.stderr.write('{}')".format(string_to_print)
        ])
        yield ret_val

    @contextmanager
    def program_that_prints_to_stdout(self, string_to_print: str) -> ScriptSourceBuilder:
        ret_val = ScriptSourceBuilder(self.language)
        ret_val.raw_script_statements([
            'import sys',
            "sys.stdout.write('{}')".format(string_to_print)
        ])
        yield ret_val

    @contextmanager
    def program_that_exits_with_code(self, exit_code: int):
        ret_val = ScriptSourceBuilder(self.language)
        ret_val.raw_script_statements([
            'import sys',
            "sys.exit({})".format(exit_code)
        ])
        yield ret_val

    @contextmanager
    def program_that_prints_cwd_without_new_line_to_stdout(self):
        ret_val = ScriptSourceBuilder(self.language)
        ret_val.raw_script_statements([
            'import sys',
            'import os',
            "sys.stdout.write(os.getcwd())"
        ])
        yield ret_val

    @contextmanager
    def program_that_prints_value_of_environment_variable_to_stdout(self, var_name: str) -> ScriptSourceBuilder:
        ret_val = ScriptSourceBuilder(self.language)
        ret_val.raw_script_statements([
            'import sys',
            'import os',
            "sys.stdout.write(os.environ['{}'])".format(var_name)
        ])
        yield ret_val


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCases))
    return ret_val


if __name__ == '__main__':
    unittest.main()
