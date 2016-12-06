import os
import pathlib
import unittest
from contextlib import contextmanager

from exactly_lib.act_phase_setups import command_line as sut
from exactly_lib.processing.parse.act_phase_source_parser import SourceCodeInstruction
from exactly_lib.section_document.syntax import LINE_COMMENT_MARKER
from exactly_lib.test_case.os_services import ACT_PHASE_OS_PROCESS_EXECUTOR
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.line_source import LineSequence
from exactly_lib_test.act_phase_setups.test_resources.act_source_and_executor import Configuration, \
    suite_for_execution
from exactly_lib_test.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_resources.programs import shell_commands
from exactly_lib_test.test_resources.programs.python_program_execution import abs_path_to_interpreter_quoted_for_exactly


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestValidation))
    ret_val.addTest(suite_for_execution(TheConfiguration()))
    return ret_val


class TestValidation(unittest.TestCase):
    def __init__(self, method_name):
        super().__init__(method_name)
        self.constructor = sut.Constructor()
        self.home_dir_as_current_dir = pathlib.Path()
        self.pre_sds_env = InstructionEnvironmentForPreSdsStep(self.home_dir_as_current_dir, dict(os.environ))

    def test_fails_when_command_is_empty(self):
        act_phase_instructions = [instr([_shell_command_source_line_for(''), ])]
        actual = self._do_validate_pre_sds(act_phase_instructions)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      actual.status,
                      'Validation result')

    def test_fails_when_command_is_only_space(self):
        act_phase_instructions = [instr([_shell_command_source_line_for('    '), ])]
        actual = self._do_validate_pre_sds(act_phase_instructions)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      actual.status,
                      'Validation result')

    def test_succeeds_when_there_is_exactly_one_statement_but_surrounded_by_empty_and_comment_lines(self):
        existing_file = abs_path_to_interpreter_quoted_for_exactly()
        act_phase_instructions = [instr(['',
                                         '             ',
                                         LINE_COMMENT_MARKER + ' line comment text',
                                         _shell_command_source_line_for(existing_file),
                                         LINE_COMMENT_MARKER + ' line comment text',
                                         ''])]
        actual = self._do_validate_pre_sds(act_phase_instructions)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                      actual.status,
                      'Validation result')

    def _do_validate_pre_sds(self, act_phase_instructions: list) -> svh.SuccessOrValidationErrorOrHardError:
        executor = self.constructor.apply(ACT_PHASE_OS_PROCESS_EXECUTOR, self.pre_sds_env, act_phase_instructions)
        return executor.validate_pre_sds(self.pre_sds_env)


class TheConfiguration(Configuration):
    def __init__(self):
        super().__init__(sut.Constructor())

    @contextmanager
    def program_that_copes_stdin_to_stdout(self) -> list:
        yield self._instruction_for(shell_commands.command_that_copes_stdin_to_stdout())

    @contextmanager
    def program_that_prints_to_stderr(self, string_to_print: str) -> list:
        yield self._instruction_for(shell_commands.command_that_prints_to_stderr(string_to_print))

    @contextmanager
    def program_that_prints_to_stdout(self, string_to_print: str) -> list:
        yield self._instruction_for(shell_commands.command_that_prints_to_stdout(string_to_print))

    @contextmanager
    def program_that_exits_with_code(self, exit_code: int) -> list:
        yield self._instruction_for(shell_commands.command_that_exits_with_code(exit_code))

    @contextmanager
    def program_that_prints_cwd_without_new_line_to_stdout(self) -> list:
        yield self._instruction_for(shell_commands.command_that_prints_cwd_without_new_line_to_stdout())

    @contextmanager
    def program_that_prints_value_of_environment_variable_to_stdout(self, var_name: str) -> list:
        yield self._instruction_for(
            shell_commands.command_that_prints_value_of_environment_variable_to_stdout(var_name))

    @contextmanager
    def program_that_sleeps_at_least(self, number_of_seconds: int) -> list:
        yield self._instruction_for(
            shell_commands.program_that_sleeps_at_least(number_of_seconds))

    @staticmethod
    def _instruction_for(command: str) -> list:
        return [SourceCodeInstruction(LineSequence(1, (_shell_command_source_line_for(command),)))]


def _shell_command_source_line_for(command: str) -> str:
    return sut.SHELL_COMMAND_MARKER + ' ' + command


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
