from contextlib import contextmanager

from exactly_lib.test_case.act_phase_handling import ActSourceAndExecutorConstructor
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
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
    def program_that_copes_stdin_to_stdout(self, hds: HomeDirectoryStructure) -> list:
        yield _instructions_for_file_in_home_act_dir(hds,
                                                     py_program.copy_stdin_to_stdout())

    @contextmanager
    def program_that_prints_to_stderr(self, hds: HomeDirectoryStructure, string_to_print: str) -> list:
        yield _instructions_for_file_in_home_act_dir(hds,
                                                     py_program.write_string_to_stderr(string_to_print))

    @contextmanager
    def program_that_prints_to_stdout(self, hds: HomeDirectoryStructure, string_to_print: str) -> list:
        yield _instructions_for_file_in_home_act_dir(hds,
                                                     py_program.write_string_to_stdout(string_to_print))

    @contextmanager
    def program_that_exits_with_code(self, hds: HomeDirectoryStructure, exit_code: int) -> list:
        yield _instructions_for_file_in_home_act_dir(hds,
                                                     py_program.exit_with_code(exit_code))

    @contextmanager
    def program_that_prints_cwd_without_new_line_to_stdout(self, hds: HomeDirectoryStructure) -> list:
        yield _instructions_for_file_in_home_act_dir(hds,
                                                     py_program.write_cwd_to_stdout())

    @contextmanager
    def program_that_prints_value_of_environment_variable_to_stdout(self, hds: HomeDirectoryStructure,
                                                                    var_name: str) -> list:
        yield _instructions_for_file_in_home_act_dir(hds,
                                                     py_program.write_value_of_environment_variable_to_stdout(
                                                         var_name))

    @contextmanager
    def program_that_sleeps_at_least(self, number_of_seconds: int) -> TestCaseSourceSetup:
        program_lines = py_program.program_that_sleeps_at_least_and_then_exists_with_zero_exit_status(number_of_seconds)
        yield TestCaseSourceSetup(
            act_phase_instructions=[instr(['sut.py'])],
            home_act_dir_contents=DirContents([File('sut.py',
                                                    lines_content(program_lines))]))


def _instructions_for_file_in_home_act_dir(hds: HomeDirectoryStructure, statements: list) -> list:
    sut_path = hds.act_dir / 'sut.py'
    with sut_path.open('w') as f:
        f.write(lines_content(statements))
    return [instr(['sut.py'])]
