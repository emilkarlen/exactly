import pathlib
import unittest
from typing import List

from exactly_lib.actors.source_interpreter import executable_file as sut, python3
from exactly_lib.actors.source_interpreter.source_file_management import SourceFileManager, \
    SourceInterpreterSetup
from exactly_lib.type_system.logic.program.process_execution.command import ProgramAndArguments
from exactly_lib_test.actors.source_interpreter import common_tests
from exactly_lib_test.actors.test_resources.action_to_check import \
    Configuration, suite_for_execution, TestCaseSourceSetup
from exactly_lib_test.actors.test_resources.integration_check import Arrangement, Expectation, \
    check_execution
from exactly_lib_test.execution.test_resources import eh_assertions
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.util.test_resources import py_program


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_execution(TheConfiguration()),
        unittest.makeSuite(TestWhenInterpreterDoesNotExistThanExecuteShouldGiveHardError),

        common_tests.suite_for(sut.actor(python3.source_interpreter_setup()),
                               is_shell=False),
    ])


class TheConfiguration(Configuration):
    def __init__(self):
        actor = sut.actor(python3.source_interpreter_setup())
        super().__init__(actor)

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


def _instructions_for(py_statements: List[str]) -> TestCaseSourceSetup:
    return TestCaseSourceSetup(
        act_phase_instructions=list(map(lambda stmt: instr([stmt]), py_statements))
    )


class TestWhenInterpreterDoesNotExistThanExecuteShouldGiveHardError(unittest.TestCase):
    def runTest(self):
        language_setup = SourceInterpreterSetup(_SourceFileManagerWithNonExistingInterpreter())
        actor = sut.actor(language_setup)
        empty_source = []
        check_execution(self,
                        actor,
                        empty_source,
                        Arrangement(),
                        Expectation(
                            execute=eh_assertions.is_hard_error)
                        )


class _SourceFileManagerWithNonExistingInterpreter(SourceFileManager):
    def command_and_args_for_executing_script_file(self, script_file_name: str) -> ProgramAndArguments:
        interpreter_path = pathlib.Path().cwd().resolve() / 'non-existing-interpreter'
        return ProgramAndArguments(str(interpreter_path),
                                   [script_file_name])

    def base_name_from_stem(self, stem: str) -> str:
        return stem + '.src'


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
