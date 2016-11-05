import pathlib
import unittest
from contextlib import contextmanager

from exactly_lib.act_phase_setups import single_command_setup as sut
from exactly_lib.section_document.syntax import LINE_COMMENT_MARKER
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.string import lines_content
from exactly_lib_test.act_phase_setups.test_resources import py_program
from exactly_lib_test.act_phase_setups.test_resources.act_phase_execution import Arrangement, Expectation, \
    check_execution
from exactly_lib_test.act_phase_setups.test_resources.act_source_and_executor import Configuration, \
    suite_for_execution
from exactly_lib_test.execution.test_resources import eh_check
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources import file_structure_utils as fs_utils
from exactly_lib_test.test_resources import python_program_execution as py_exe
from exactly_lib_test.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_resources.file_utils import tmp_file_containing_lines
from exactly_lib_test.test_resources.python_program_execution import abs_path_to_interpreter_quoted_for_exactly
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestValidation))
    ret_val.addTest(unittest.makeSuite(TestSuccessfulExecutionOfProgramRelHomeWithCommandLineArguments))
    ret_val.addTest(suite_for_execution(TheConfiguration()))
    return ret_val


class TestValidation(unittest.TestCase):
    def __init__(self, method_name):
        super().__init__(method_name)
        self.constructor = sut.Constructor()
        self.home_dir_as_current_dir = pathlib.Path()
        self.pre_eds_env = InstructionEnvironmentForPreSdsStep(self.home_dir_as_current_dir)

    def test_fails_when_there_are_no_instructions(self):
        act_phase_instructions = []
        actual = self._do_validate_pre_eds(act_phase_instructions)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      actual.status,
                      'Validation result')

    def test_fails_when_there_is_more_than_one_instruction(self):
        act_phase_instructions = [instr(['']),
                                  instr([''])]
        actual = self._do_validate_pre_eds(act_phase_instructions)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      actual.status,
                      'Validation result')

    def test_fails_when_there_are_no_statements(self):
        act_phase_instructions = [instr([''])]
        actual = self._do_validate_pre_eds(act_phase_instructions)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      actual.status,
                      'Validation result')

    def test_fails_when_there_is_more_than_one_statement(self):
        existing_file = abs_path_to_interpreter_quoted_for_exactly()
        act_phase_instructions = [instr([existing_file,
                                         existing_file])]
        actual = self._do_validate_pre_eds(act_phase_instructions)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      actual.status,
                      'Validation result')

    def test_succeeds_when_there_is_exactly_one_statement_but_surrounded_by_empty_and_comment_lines(self):
        existing_file = abs_path_to_interpreter_quoted_for_exactly()
        act_phase_instructions = [instr(['',
                                         '             ',
                                         LINE_COMMENT_MARKER + ' line comment text',
                                         existing_file,
                                         LINE_COMMENT_MARKER + ' line comment text',
                                         ''])]
        actual = self._do_validate_pre_eds(act_phase_instructions)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                      actual.status,
                      'Validation result')

    def test_validate_pre_eds_SHOULD_fail_WHEN_statement_line_is_not_an_existing_file_rel_home(self):
        act_phase_instructions = [instr(['name-of-non-existing-file'])]
        actual = self._do_validate_pre_eds(act_phase_instructions)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      actual.status,
                      'Validation result')

    def test_validate_pre_eds_SHOULD_fail_WHEN_statement_line_is_not_an_existing_file__absolute_file_name(self):
        absolute_name_of_non_existing_file = str(pathlib.Path().resolve() / 'non' / 'existing' / 'file' / 'oiasdlkv')
        act_phase_instructions = [instr([absolute_name_of_non_existing_file])]
        actual = self._do_validate_pre_eds(act_phase_instructions)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      actual.status,
                      'Validation result')

    def test_validate_pre_eds_SHOULD_succeed_WHEN_statement_line_is_absolute_name_of_existing_file_not_under_home(self):
        existing_file = abs_path_to_interpreter_quoted_for_exactly()
        act_phase_instructions = [instr([existing_file])]
        actual = self._do_validate_pre_eds(act_phase_instructions)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                      actual.status,
                      'Validation result')

    def test_validate_pre_eds_SHOULD_succeed_WHEN_statement_line_is_absolute_name_of_existing_file__and_arguments(self):
        existing_file = abs_path_to_interpreter_quoted_for_exactly()
        abs_path_and_arguments = ' '.join([existing_file, 'arg1', '"quoted arg"'])
        act_phase_instructions = [instr([abs_path_and_arguments])]
        actual = self._do_validate_pre_eds(act_phase_instructions)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                      actual.status,
                      'Validation result')

    def test_validate_pre_eds_SHOULD_succeed_WHEN_statement_line_is_relative_name_of_an_existing_file_rel_home(self):
        act_phase_instructions = [instr(['system-under-test'])]
        executor = self.constructor.apply(self.pre_eds_env, act_phase_instructions)
        with fs_utils.tmp_dir(fs.DirContents([fs.empty_file('system-under-test')])) as home_dir_path:
            actual = executor.validate_pre_sds(home_dir_path)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                      actual.status,
                      'Validation result')

    @staticmethod
    def _new_environment() -> InstructionEnvironmentForPreSdsStep:
        home_dir_path = pathlib.Path()
        return InstructionEnvironmentForPreSdsStep(home_dir_path)

    def _do_validate_pre_eds(self, act_phase_instructions: list) -> svh.SuccessOrValidationErrorOrHardError:
        executor = self.constructor.apply(self.pre_eds_env, act_phase_instructions)
        return executor.validate_pre_sds(self.pre_eds_env.home_directory)


class TheConfiguration(Configuration):
    def __init__(self):
        super().__init__(sut.Constructor())

    @contextmanager
    def program_that_copes_stdin_to_stdout(self) -> list:
        return self._builder_for_executing_source_from_py_file(py_program.copy_stdin_to_stdout())

    @contextmanager
    def program_that_prints_to_stderr(self, string_to_print: str) -> list:
        return self._builder_for_executing_source_from_py_file(py_program.write_string_to_stderr(string_to_print))

    @contextmanager
    def program_that_prints_to_stdout(self, string_to_print: str) -> list:
        return self._builder_for_executing_source_from_py_file(py_program.write_string_to_stdout(string_to_print))

    @contextmanager
    def program_that_exits_with_code(self, exit_code: int) -> list:
        return self._builder_for_executing_source_from_py_file(py_program.exit_with_code(exit_code))

    @contextmanager
    def program_that_prints_cwd_without_new_line_to_stdout(self) -> list:
        return self._builder_for_executing_source_from_py_file(py_program.write_cwd_to_stdout())

    @contextmanager
    def program_that_prints_value_of_environment_variable_to_stdout(self, var_name: str) -> list:
        return self._builder_for_executing_source_from_py_file(
            py_program.write_value_of_environment_variable_to_stdout(var_name))

    @contextmanager
    def program_that_sleeps_at_least(self, number_of_seconds: int) -> list:
        return self._builder_for_executing_source_from_py_file(
            py_program.program_that_sleeps_at_least(number_of_seconds))

    def _builder_for_executing_source_from_py_file(self, statements: list) -> list:
        with tmp_file_containing_lines(statements) as src_path:
            yield self._builder_for_executing_py_file(src_path)

    def _builder_for_executing_py_file(self, src_path: pathlib.Path) -> list:
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
