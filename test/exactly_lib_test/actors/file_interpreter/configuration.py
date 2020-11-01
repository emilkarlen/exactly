import sys
from contextlib import contextmanager
from typing import List, ContextManager

from exactly_lib.test_case.actor import Actor
from exactly_lib.test_case_utils.program.command import command_sdvs
from exactly_lib.type_val_deps.types.path import path_ddvs, path_sdvs
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib_test.actors.test_resources.action_to_check import Configuration, TestCaseSourceSetup
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.util.test_resources import py_program

COMMAND_THAT_RUNS_PYTHON_PROGRAM_FILE = command_sdvs.for_executable_file(
    path_sdvs.constant(path_ddvs.absolute_file_name(sys.executable)),
)


class TheConfigurationBase(Configuration):
    def __init__(self, actor: Actor):
        super().__init__(actor)

    def program_that_copes_stdin_to_stdout(self) -> ContextManager[TestCaseSourceSetup]:
        return _instructions_for_file_in_hds_act_dir(py_program.copy_stdin_to_stdout())

    def program_that_prints_to_stdout(self,
                                      string_to_print: str) -> ContextManager[TestCaseSourceSetup]:
        return _instructions_for_file_in_hds_act_dir(py_program.write_string_to_stdout(string_to_print))

    def program_that_prints_to_stderr(self,
                                      string_to_print: str) -> ContextManager[TestCaseSourceSetup]:
        return _instructions_for_file_in_hds_act_dir(py_program.write_string_to_stderr(string_to_print))

    def program_that_prints_value_of_environment_variable_to_stdout(
            self, var_name: str) -> ContextManager[TestCaseSourceSetup]:
        return _instructions_for_file_in_hds_act_dir(py_program.write_value_of_environment_variable_to_stdout(
            var_name))

    def program_that_prints_cwd_to_stdout(self) -> ContextManager[TestCaseSourceSetup]:
        return _instructions_for_file_in_hds_act_dir(py_program.write_cwd_to_stdout())

    def program_that_exits_with_code(self,
                                     exit_code: int) -> ContextManager[TestCaseSourceSetup]:
        return _instructions_for_file_in_hds_act_dir(py_program.exit_with_code(exit_code))

    def program_that_sleeps_at_least(self, number_of_seconds: int) -> ContextManager[TestCaseSourceSetup]:
        return _instructions_for_file_in_hds_act_dir(
            py_program.program_that_sleeps_at_least_and_then_exists_with_zero_exit_status(number_of_seconds)
        )


@contextmanager
def _instructions_for_file_in_hds_act_dir(py_src: List[str]) -> ContextManager[TestCaseSourceSetup]:
    file_name_rel_hds_act = 'the-program'
    yield TestCaseSourceSetup(
        act_phase_instructions=[instr([file_name_rel_hds_act])],
        home_act_dir_contents=DirContents([
            fs.python_executable_file(file_name_rel_hds_act,
                                      lines_content(py_src))
        ])
    )
