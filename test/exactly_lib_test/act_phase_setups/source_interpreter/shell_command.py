import shlex
import sys
import unittest
from contextlib import contextmanager

from exactly_lib.act_phase_setups.source_interpreter import shell_command as sut
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib_test.act_phase_setups.source_interpreter import common_tests
from exactly_lib_test.act_phase_setups.test_resources.act_source_and_executor import \
    Configuration, suite_for_execution, TestCaseSourceSetup
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_resources.programs.python_program_execution import file_name_of_interpreter
from exactly_lib_test.util.test_resources import py_program


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_execution(TheConfiguration()),
        common_tests.suite_for(sut.Constructor(shlex.quote(sys.executable)),
                               is_shell=True)
    ])


class TheConfiguration(Configuration):
    def __init__(self):
        self.setup = sut.handling_for_interpreter_command(file_name_of_interpreter())
        super().__init__(self.setup.source_and_executor_constructor)

    @contextmanager
    def program_that_copes_stdin_to_stdout(self, hds: HomeDirectoryStructure) -> list:
        yield _instructions_for(py_program.copy_stdin_to_stdout())

    @contextmanager
    def program_that_prints_to_stderr(self,
                                      hds: HomeDirectoryStructure,
                                      string_to_print: str) -> list:
        yield _instructions_for(py_program.write_string_to_stderr(string_to_print))

    @contextmanager
    def program_that_prints_to_stdout(self,
                                      hds: HomeDirectoryStructure,
                                      string_to_print: str) -> list:
        yield _instructions_for(py_program.write_string_to_stdout(string_to_print))

    @contextmanager
    def program_that_exits_with_code(self,
                                     hds: HomeDirectoryStructure,
                                     exit_code: int) -> list:
        yield _instructions_for(py_program.exit_with_code(exit_code))

    @contextmanager
    def program_that_prints_cwd_without_new_line_to_stdout(self, hds: HomeDirectoryStructure) -> list:
        yield _instructions_for(py_program.write_cwd_to_stdout())

    @contextmanager
    def program_that_prints_value_of_environment_variable_to_stdout(self,
                                                                    hds: HomeDirectoryStructure,
                                                                    var_name: str) -> list:
        yield _instructions_for(py_program.write_value_of_environment_variable_to_stdout(var_name))

    @contextmanager
    def program_that_sleeps_at_least(self, number_of_seconds: int) -> TestCaseSourceSetup:
        yield TestCaseSourceSetup(act_phase_instructions=_instructions_for(
            py_program.program_that_sleeps_at_least_and_then_exists_with_zero_exit_status(number_of_seconds)))


def _instructions_for(statements: list) -> list:
    return list(map(lambda stmt: instr([stmt]), statements))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
