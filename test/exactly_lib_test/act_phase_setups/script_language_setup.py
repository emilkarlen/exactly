import pathlib
import unittest
from contextlib import contextmanager

from exactly_lib.act_phase_setups.script_interpretation import script_language_setup as sut, python3
from exactly_lib.act_phase_setups.script_interpretation.generic_script_language import StandardScriptLanguage
from exactly_lib.act_phase_setups.script_interpretation.script_language_management import ScriptFileManager, \
    ScriptLanguageSetup
from exactly_lib.test_case.phases.act.program_source import ActSourceBuilder, ActSourceBuilderForPlainStringsBase
from exactly_lib_test.act_phase_setups.test_resources import py_program
from exactly_lib_test.act_phase_setups.test_resources.act_program_executor import \
    Configuration, suite_for_execution, run_execute


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_execution(TheConfiguration()),
        unittest.makeSuite(TestWhenInterpreterDoesNotExistThanTheResultShouldBeHardError)
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class TheConfiguration(Configuration):
    def __init__(self):
        self.setup = sut.new_for_script_language_setup(python3.script_language_setup())
        super().__init__(self.setup.executor)

    @contextmanager
    def program_that_copes_stdin_to_stdout(self) -> ActSourceBuilder:
        yield self._builder_for(py_program.copy_stdin_to_stdout())

    @contextmanager
    def program_that_prints_to_stderr(self, string_to_print: str) -> ActSourceBuilder:
        yield self._builder_for(py_program.write_string_to_stderr(string_to_print))

    @contextmanager
    def program_that_prints_to_stdout(self, string_to_print: str) -> ActSourceBuilder:
        yield self._builder_for(py_program.write_string_to_stdout(string_to_print))

    @contextmanager
    def program_that_exits_with_code(self, exit_code: int):
        yield self._builder_for(py_program.exit_with_code(exit_code))

    @contextmanager
    def program_that_prints_cwd_without_new_line_to_stdout(self):
        yield self._builder_for(py_program.write_cwd_to_stdout())

    @contextmanager
    def program_that_prints_value_of_environment_variable_to_stdout(self, var_name: str) -> ActSourceBuilder:
        yield self._builder_for(py_program.write_value_of_environment_variable_to_stdout(var_name))

    def _builder_for(self, statements: list) -> ActSourceBuilder:
        ret_val = self.setup.script_builder_constructor()
        ret_val.raw_script_statements(statements)
        return ret_val


class TestWhenInterpreterDoesNotExistThanTheResultShouldBeHardError(unittest.TestCase):
    def runTest(self):
        language_setup = ScriptLanguageSetup(_ScriptFileManagerWithNonExistingInterpreter(),
                                             StandardScriptLanguage())
        executor = sut.ActSourceExecutorForScriptLanguage(language_setup)
        empty_source = ActSourceBuilderForPlainStringsBase()
        exit_code_or_hard_error = run_execute(self, executor, empty_source)
        self.assertTrue(exit_code_or_hard_error.is_hard_error,
                        'Expecting a HARD ERROR')


class _ScriptFileManagerWithNonExistingInterpreter(ScriptFileManager):
    def command_and_args_for_executing_script_file(self, script_file_name: str) -> list:
        interpreter_path = pathlib.Path().cwd().resolve() / 'non-existing-interpreter'
        return [str(interpreter_path), script_file_name]

    def base_name_from_stem(self, stem: str) -> str:
        return stem + '.src'
