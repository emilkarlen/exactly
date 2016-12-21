import pathlib
import unittest
from contextlib import contextmanager

from exactly_lib.act_phase_setups import command_line as sut
from exactly_lib.util.string import lines_content
from exactly_lib_test.act_phase_setups.test_resources import py_program
from exactly_lib_test.act_phase_setups.test_resources import \
    test_validation_for_single_file_rel_home as single_file_rel_home
from exactly_lib_test.act_phase_setups.test_resources import \
    test_validation_for_single_line_source as single_line_source
from exactly_lib_test.act_phase_setups.test_resources.act_phase_execution import Arrangement, Expectation, \
    check_execution
from exactly_lib_test.act_phase_setups.test_resources.act_source_and_executor import Configuration, \
    suite_for_execution
from exactly_lib_test.execution.test_resources import eh_check
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources.file_utils import tmp_file_containing_lines
from exactly_lib_test.test_resources.programs import python_program_execution as py_exe
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    configuration = TheConfiguration()
    ret_val.addTest(single_line_source.suite_for(configuration))
    ret_val.addTest(single_file_rel_home.suite_for(configuration))
    ret_val.addTest(unittest.makeSuite(TestSuccessfulExecutionOfProgramRelHomeWithCommandLineArguments))
    ret_val.addTest(suite_for_execution(configuration))
    return ret_val


class TheConfiguration(Configuration):
    def __init__(self):
        super().__init__(sut.Constructor())

    @contextmanager
    def program_that_copes_stdin_to_stdout(self, home_dir_path: pathlib.Path) -> list:
        return self._instructions_for_executing_source_from_py_file(py_program.copy_stdin_to_stdout())

    @contextmanager
    def program_that_prints_to_stderr(self, home_dir_path: pathlib.Path, string_to_print: str) -> list:
        return self._instructions_for_executing_source_from_py_file(py_program.write_string_to_stderr(string_to_print))

    @contextmanager
    def program_that_prints_to_stdout(self, home_dir_path: pathlib.Path, string_to_print: str) -> list:
        return self._instructions_for_executing_source_from_py_file(py_program.write_string_to_stdout(string_to_print))

    @contextmanager
    def program_that_exits_with_code(self, home_dir_path: pathlib.Path, exit_code: int) -> list:
        return self._instructions_for_executing_source_from_py_file(py_program.exit_with_code(exit_code))

    @contextmanager
    def program_that_prints_cwd_without_new_line_to_stdout(self, home_dir_path: pathlib.Path) -> list:
        return self._instructions_for_executing_source_from_py_file(py_program.write_cwd_to_stdout())

    @contextmanager
    def program_that_prints_value_of_environment_variable_to_stdout(self, home_dir_path: pathlib.Path,
                                                                    var_name: str) -> list:
        return self._instructions_for_executing_source_from_py_file(
            py_program.write_value_of_environment_variable_to_stdout(var_name))

    @contextmanager
    def program_that_sleeps_at_least(self, home_dir_path: pathlib.Path, number_of_seconds: int) -> list:
        return self._instructions_for_executing_source_from_py_file(
            py_program.program_that_sleeps_at_least_and_then_exists_with_zero_exit_status(number_of_seconds))

    def _instructions_for_executing_source_from_py_file(self, statements: list) -> list:
        with tmp_file_containing_lines(statements) as src_path:
            yield _instructions_for_executing_py_file(src_path)


def _instructions_for_executing_py_file(src_path: pathlib.Path) -> list:
    cmd = py_exe.command_line_for_interpreting(src_path)
    return [instr([cmd])]


class TestSuccessfulExecutionOfProgramRelHomeWithCommandLineArguments(unittest.TestCase):
    _PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES = """\
import sys
for arg in sys.argv[1:]:
  print(arg)
"""

    def runTest(self):
        executor_constructor = sut.Constructor()
        act_phase_instructions = [
            instr(['system-under-test first-argument "quoted argument"'])
        ]
        arrangement = Arrangement(executor_constructor,
                                  act_phase_instructions,
                                  home_dir_contents=fs.DirContents([
                                      fs.python_executable_file(
                                          'system-under-test',
                                          self._PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES)
                                  ]))
        expected_output = lines_content(['first-argument',
                                         'quoted argument'])
        expectation = Expectation(result_of_execute=eh_check.is_exit_code(0),
                                  sub_process_result_from_execute=pr.stdout(va.Equals(expected_output,
                                                                                      'CLI arguments, one per line')))
        check_execution(self, arrangement, expectation)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
