import shlex
import sys
import unittest
from typing import List

from exactly_lib.actors.source_interpreter import shell_command as sut
from exactly_lib.actors.source_interpreter.shell_command import actor
from exactly_lib_test.actors.source_interpreter import common_tests
from exactly_lib_test.actors.test_resources.action_to_check import \
    Configuration, suite_for_execution, TestCaseSourceSetup
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_resources.programs.python_program_execution import file_name_of_interpreter
from exactly_lib_test.util.test_resources import py_program


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_execution(TheConfiguration()),
        common_tests.suite_for(sut.actor(shlex.quote(sys.executable)),
                               is_shell=True)
    ])


class TheConfiguration(Configuration):
    def __init__(self):
        command = file_name_of_interpreter()
        self.setup = actor(command)
        super().__init__(self.setup)

    def program_that_exits_with_code(self,
                                     exit_code: int) -> TestCaseSourceSetup:
        return _instructions_for(py_program.exit_with_code(exit_code))

    def program_that_copes_stdin_to_stdout(self) -> TestCaseSourceSetup:
        return _instructions_for(py_program.copy_stdin_to_stdout())

    def program_that_prints_to_stdout(self,
                                      string_to_print: str) -> TestCaseSourceSetup:
        return _instructions_for(py_program.write_string_to_stdout(string_to_print))

    def program_that_prints_to_stderr(self,
                                      string_to_print: str) -> TestCaseSourceSetup:
        return _instructions_for(py_program.write_string_to_stderr(string_to_print))

    def program_that_prints_value_of_environment_variable_to_stdout(self, var_name: str) -> TestCaseSourceSetup:
        return _instructions_for(py_program.write_value_of_environment_variable_to_stdout(var_name))

    def program_that_prints_cwd_to_stdout(self) -> TestCaseSourceSetup:
        return _instructions_for(py_program.write_cwd_to_stdout())

    def program_that_sleeps_at_least(self, number_of_seconds: int) -> TestCaseSourceSetup:
        return _instructions_for(
            py_program.program_that_sleeps_at_least_and_then_exists_with_zero_exit_status(number_of_seconds)
        )


def _instructions_for(statements: List[str]) -> TestCaseSourceSetup:
    return TestCaseSourceSetup(
        act_phase_instructions=list(map(lambda stmt: instr([stmt]), statements))
    )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
