import pathlib
import unittest
from contextlib import contextmanager

from exactly_lib.act_phase_setups import single_command_setup as sut
from exactly_lib.section_document.syntax import LINE_COMMENT_MARKER
from exactly_lib.test_case.phases.act.program_source import ActSourceBuilder, ActSourceBuilderForStatementLines
from exactly_lib.test_case.phases.common import GlobalEnvironmentForPreEdsStep
from exactly_lib.test_case.phases.result import svh
from exactly_lib_test.act_phase_setups.test_resources import py_program
from exactly_lib_test.act_phase_setups.test_resources.act_source_and_executor import Configuration, \
    suite_for_execution, check_execution, Arrangement, Expectation
from exactly_lib_test.execution.test_resources import eh_check
from exactly_lib_test.test_resources import python_program_execution as py_exe
from exactly_lib_test.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_resources.file_utils import tmp_file_containing_lines


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestValidation))
    ret_val.addTest(unittest.makeSuite(TestWhenInterpreterDoesNotExistThanExecuteShouldGiveHardError))
    ret_val.addTest(suite_for_execution(TheConfiguration()))
    return ret_val


class TestValidation(unittest.TestCase):
    def __init__(self, method_name):
        super().__init__(method_name)
        self.constructor = sut.Constructor()
        self.home_dir_as_current_dir = pathlib.Path()
        self.pre_eds_env = GlobalEnvironmentForPreEdsStep(self.home_dir_as_current_dir)

    def test_fails_when_there_are_no_instructions(self):
        act_phase_instructions = []
        actual = self._do_validate_pre_eds(act_phase_instructions)
        self.assertIs(actual.status,
                      svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      'Validation result')

    def test_fails_when_there_is_more_than_one_instruction(self):
        act_phase_instructions = [instr(['']),
                                  instr([''])]
        actual = self._do_validate_pre_eds(act_phase_instructions)
        self.assertIs(actual.status,
                      svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      'Validation result')

    def test_fails_when_there_are_no_statements(self):
        act_phase_instructions = [instr([''])]
        actual = self._do_validate_pre_eds(act_phase_instructions)
        self.assertIs(actual.status,
                      svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      'Validation result')

    def test_fails_when_there_is_more_than_one_statement(self):
        act_phase_instructions = [instr(['statement 1',
                                         'statement 2'])]
        actual = self._do_validate_pre_eds(act_phase_instructions)
        self.assertIs(actual.status,
                      svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      'Validation result')

    def test_succeeds_when_there_is_exactly_one_statement(self):
        act_phase_instructions = [instr(['statement 1'])]
        actual = self._do_validate_pre_eds(act_phase_instructions)
        self.assertIs(actual.status,
                      svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                      'Validation result')

    def test_succeeds_when_there_is_exactly_one_statement_but_surrounded_by_empty_and_comment_lines(self):
        act_phase_instructions = [instr(['',
                                         '             ',
                                         LINE_COMMENT_MARKER + ' line comment text',
                                         'statement 1',
                                         LINE_COMMENT_MARKER + ' line comment text',
                                         ''])]
        actual = self._do_validate_pre_eds(act_phase_instructions)
        self.assertIs(actual.status,
                      svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                      'Validation result')

    @staticmethod
    def _new_environment() -> GlobalEnvironmentForPreEdsStep:
        home_dir_path = pathlib.Path()
        return GlobalEnvironmentForPreEdsStep(home_dir_path)

    def _do_validate_pre_eds(self, act_phase_instructions: list) -> svh.SuccessOrValidationErrorOrHardError:
        executor = self.constructor.apply(self.pre_eds_env, act_phase_instructions)
        return executor.validate_pre_eds(self.pre_eds_env.home_directory)


class TheConfiguration(Configuration):
    def __init__(self):
        super().__init__(sut.Constructor())

    @contextmanager
    def program_that_copes_stdin_to_stdout(self) -> ActSourceBuilder:
        return self._builder_for_executing_source_from_py_file(py_program.copy_stdin_to_stdout())

    @contextmanager
    def program_that_prints_to_stderr(self, string_to_print: str) -> ActSourceBuilder:
        return self._builder_for_executing_source_from_py_file(py_program.write_string_to_stderr(string_to_print))

    @contextmanager
    def program_that_prints_to_stdout(self, string_to_print: str) -> ActSourceBuilder:
        return self._builder_for_executing_source_from_py_file(py_program.write_string_to_stdout(string_to_print))

    @contextmanager
    def program_that_exits_with_code(self, exit_code: int):
        return self._builder_for_executing_source_from_py_file(py_program.exit_with_code(exit_code))

    @contextmanager
    def program_that_prints_cwd_without_new_line_to_stdout(self):
        return self._builder_for_executing_source_from_py_file(py_program.write_cwd_to_stdout())

    @contextmanager
    def program_that_prints_value_of_environment_variable_to_stdout(self, var_name: str) -> ActSourceBuilder:
        return self._builder_for_executing_source_from_py_file(
            py_program.write_value_of_environment_variable_to_stdout(var_name))

    def _builder_for_executing_source_from_py_file(self, statements: list) -> ActSourceBuilder:
        with tmp_file_containing_lines(statements) as src_path:
            yield self._builder_for_executing_py_file(src_path)

    def _builder_for_executing_py_file(self, src_path: pathlib.Path) -> ActSourceBuilder:
        ret_val = self.setup.script_builder_constructor()
        cmd = py_exe.command_line_for_interpreting(src_path)
        ret_val.raw_script_statement(cmd)
        return ret_val


class TestWhenInterpreterDoesNotExistThanExecuteShouldGiveHardError(unittest.TestCase):
    def runTest(self):
        executor = sut.ActSourceExecutorForSingleCommand()
        source = self._source_that_references_non_existing_program()
        check_execution(self,
                        Arrangement(executor,
                                    source),
                        Expectation(result_of_execute=eh_check.is_hard_error))

    def _source_that_references_non_existing_program(self) -> ActSourceBuilderForStatementLines:
        source = ActSourceBuilderForStatementLines()
        interpreter_path = pathlib.Path().cwd().resolve() / 'non-existing-interpreter'
        source.raw_script_statement(str(interpreter_path))
        return source


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
