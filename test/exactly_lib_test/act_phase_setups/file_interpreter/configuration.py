import pathlib
from contextlib import contextmanager

from exactly_lib.test_case.act_phase_handling import ActSourceAndExecutorConstructor
from exactly_lib.util.string import lines_content
from exactly_lib_test.act_phase_setups.test_resources.act_source_and_executor import Configuration, TestCaseSourceSetup
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_case_utils.test_resources import py_program
from exactly_lib_test.test_resources.file_structure import DirContents
from exactly_lib_test.test_resources.file_structure import File


class TheConfigurationBase(Configuration):
    def __init__(self, constructor: ActSourceAndExecutorConstructor):
        super().__init__(constructor)

    @contextmanager
    def program_that_copes_stdin_to_stdout(self, home_dir_path: pathlib.Path) -> list:
        yield _instructions_for_file_in_home_dir(home_dir_path,
                                                 py_program.copy_stdin_to_stdout())

    @contextmanager
    def program_that_prints_to_stderr(self, home_dir_path: pathlib.Path, string_to_print: str) -> list:
        yield _instructions_for_file_in_home_dir(home_dir_path,
                                                 py_program.write_string_to_stderr(string_to_print))

    @contextmanager
    def program_that_prints_to_stdout(self, home_dir_path: pathlib.Path, string_to_print: str) -> list:
        yield _instructions_for_file_in_home_dir(home_dir_path,
                                                 py_program.write_string_to_stdout(string_to_print))

    @contextmanager
    def program_that_exits_with_code(self, home_dir_path: pathlib.Path, exit_code: int) -> list:
        yield _instructions_for_file_in_home_dir(home_dir_path,
                                                 py_program.exit_with_code(exit_code))

    @contextmanager
    def program_that_prints_cwd_without_new_line_to_stdout(self, home_dir_path: pathlib.Path) -> list:
        yield _instructions_for_file_in_home_dir(home_dir_path,
                                                 py_program.write_cwd_to_stdout())

    @contextmanager
    def program_that_prints_value_of_environment_variable_to_stdout(self, home_dir_path: pathlib.Path,
                                                                    var_name: str) -> list:
        yield _instructions_for_file_in_home_dir(home_dir_path,
                                                 py_program.write_value_of_environment_variable_to_stdout(
                                                     var_name))

    @contextmanager
    def program_that_sleeps_at_least(self, number_of_seconds: int) -> TestCaseSourceSetup:
        program_lines = py_program.program_that_sleeps_at_least_and_then_exists_with_zero_exit_status(number_of_seconds)
        yield TestCaseSourceSetup([instr(['sut.py'])],
                                  DirContents([File('sut.py',
                                                    lines_content(program_lines))]))


def _instructions_for_file_in_home_dir(home_dir_path: pathlib.Path, statements: list) -> list:
    with open(str(home_dir_path / 'sut.py'), 'w') as f:
        f.write(lines_content(statements))
    return [instr(['sut.py'])]
