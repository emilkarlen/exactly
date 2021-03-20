import pathlib
import unittest
from contextlib import contextmanager
from typing import List, ContextManager

from exactly_lib.impls.actors.source_interpreter import actor as sut
from exactly_lib.impls.types.program.command import command_sdvs
from exactly_lib.type_val_deps.types.path import path_ddvs, path_sdvs
from exactly_lib.type_val_deps.types.program.sdv.command import CommandSdv
from exactly_lib_test.impls.actors.test_resources import python3
from exactly_lib_test.impls.actors.test_resources.action_to_check import \
    Configuration, suite_for_execution, TestCaseSourceSetup
from exactly_lib_test.impls.actors.test_resources.integration_check import Expectation, \
    check_execution, arrangement_w_tcds
from exactly_lib_test.type_val_deps.test_resources.validation.svh_validation import ValidationExpectationSvh
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.util.test_resources import py_program


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_execution(TheConfiguration()),
        unittest.makeSuite(TestValidationErrorWhenInterpreterDoesNotExist),
    ])


class TheConfiguration(Configuration):
    def __init__(self):
        actor = sut.actor(python3.python_command())
        super().__init__(actor)

    def program_that_exits_with_code(self,
                                     exit_code: int) -> ContextManager[TestCaseSourceSetup]:
        return _instructions_for(py_program.exit_with_code(exit_code))

    def program_that_copes_stdin_to_stdout(self) -> ContextManager[TestCaseSourceSetup]:
        return _instructions_for(py_program.copy_stdin_to_stdout())

    def program_that_prints_to_stdout(self,
                                      string_to_print: str) -> ContextManager[TestCaseSourceSetup]:
        return _instructions_for(py_program.write_string_to_stdout(string_to_print))

    def program_that_prints_to_stderr(self,
                                      string_to_print: str) -> ContextManager[TestCaseSourceSetup]:
        return _instructions_for(py_program.write_string_to_stderr(string_to_print))

    def program_that_prints_value_of_environment_variable_to_stdout(
            self, var_name: str) -> ContextManager[TestCaseSourceSetup]:
        return _instructions_for(py_program.write_value_of_environment_variable_to_stdout(var_name))

    def program_that_prints_cwd_to_stdout(self) -> ContextManager[TestCaseSourceSetup]:
        return _instructions_for(py_program.write_cwd_to_stdout())

    def program_that_sleeps_at_least(self, number_of_seconds: int) -> ContextManager[TestCaseSourceSetup]:
        return _instructions_for(
            py_program.program_that_sleeps_at_least_and_then_exists_with_zero_exit_status(number_of_seconds)
        )


@contextmanager
def _instructions_for(py_statements: List[str]) -> ContextManager[TestCaseSourceSetup]:
    yield TestCaseSourceSetup(
        act_phase_instructions=list(map(lambda stmt: instr([stmt]), py_statements))
    )


class TestValidationErrorWhenInterpreterDoesNotExist(unittest.TestCase):
    def runTest(self):
        actor = sut.actor(_command_for_non_existing_interpreter())
        empty_source = []
        check_execution(self,
                        actor,
                        empty_source,
                        arrangement_w_tcds(),
                        Expectation(
                            validation=ValidationExpectationSvh.fails__pre_sds()
                        )
                        )


def _command_for_non_existing_interpreter() -> CommandSdv:
    interpreter_path = pathlib.Path().cwd().resolve() / 'non-existing-interpreter'
    return command_sdvs.for_executable_file(
        path_sdvs.constant(path_ddvs.absolute_path(interpreter_path))
    )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
