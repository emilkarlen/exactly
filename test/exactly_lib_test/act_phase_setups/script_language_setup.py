import pathlib
import unittest
from contextlib import contextmanager

from exactly_lib.act_phase_setups.script_interpretation import script_language_setup as sut, python3
from exactly_lib.act_phase_setups.script_interpretation.generic_script_language import StandardScriptLanguage
from exactly_lib.act_phase_setups.script_interpretation.script_language_management import ScriptFileManager, \
    ScriptLanguageSetup
from exactly_lib.util.string import lines_content
from exactly_lib_test.act_phase_setups.test_resources import py_program
from exactly_lib_test.act_phase_setups.test_resources.act_source_and_executor import \
    Configuration, suite_for_execution, check_execution, Arrangement, Expectation
from exactly_lib_test.execution.test_resources import eh_check
from exactly_lib_test.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_resources.execution.eds_contents_check import TestCaseRootContainsExactly
from exactly_lib_test.test_resources.file_structure import DirContents, File


class TheConfiguration(Configuration):
    def __init__(self):
        self.setup = sut.new_for_script_language_setup(python3.script_language_setup())
        super().__init__(self.setup.source_and_executor_constructor)

    @contextmanager
    def program_that_copes_stdin_to_stdout(self) -> list:
        yield self._builder_for(py_program.copy_stdin_to_stdout())

    @contextmanager
    def program_that_prints_to_stderr(self, string_to_print: str) -> list:
        yield self._builder_for(py_program.write_string_to_stderr(string_to_print))

    @contextmanager
    def program_that_prints_to_stdout(self, string_to_print: str) -> list:
        yield self._builder_for(py_program.write_string_to_stdout(string_to_print))

    @contextmanager
    def program_that_exits_with_code(self, exit_code: int) -> list:
        yield self._builder_for(py_program.exit_with_code(exit_code))

    @contextmanager
    def program_that_prints_cwd_without_new_line_to_stdout(self) -> list:
        yield self._builder_for(py_program.write_cwd_to_stdout())

    @contextmanager
    def program_that_prints_value_of_environment_variable_to_stdout(self, var_name: str) -> list:
        yield self._builder_for(py_program.write_value_of_environment_variable_to_stdout(var_name))

    def _builder_for(self, statements: list) -> list:
        return list(map(lambda stmt: instr([stmt]), statements))


class TestWhenInterpreterDoesNotExistThanExecuteShouldGiveHardError(unittest.TestCase):
    def runTest(self):
        language_setup = ScriptLanguageSetup(_ScriptFileManagerWithNonExistingInterpreter(),
                                             StandardScriptLanguage())
        act_phase_setup = sut.new_for_script_language_setup(language_setup)
        empty_source = []
        check_execution(self,
                        Arrangement(act_phase_setup.source_and_executor_constructor,
                                    empty_source),
                        Expectation(result_of_execute=eh_check.is_hard_error))


class TestThatScriptSourceIsWrittenToTestCaseDir(unittest.TestCase):
    def runTest(self):
        language_setup = ScriptLanguageSetup(_ScriptFileManagerWithNonExistingInterpreter(),
                                             StandardScriptLanguage())
        act_phase_setup = sut.new_for_script_language_setup(language_setup)
        source = [instr(['print(1)'])]
        expected_file_name = language_setup.base_name_from_stem(sut.ActSourceExecutorForScriptLanguage.FILE_NAME_STEM)
        exit_code_or_hard_error = check_execution(
            self,
            Arrangement(act_phase_setup.source_and_executor_constructor, source),
            Expectation(result_of_execute=eh_check.is_hard_error,
                        side_effects_on_files_after_execute=TestCaseRootContainsExactly(DirContents([
                            File(expected_file_name,
                                 lines_content(['print(1)']))
                        ]))))
        self.assertTrue(exit_code_or_hard_error.is_hard_error,
                        'Expecting a HARD ERROR')


class _ScriptFileManagerWithNonExistingInterpreter(ScriptFileManager):
    def command_and_args_for_executing_script_file(self, script_file_name: str) -> list:
        interpreter_path = pathlib.Path().cwd().resolve() / 'non-existing-interpreter'
        return [str(interpreter_path), script_file_name]

    def base_name_from_stem(self, stem: str) -> str:
        return stem + '.src'


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_execution(TheConfiguration()),
        unittest.makeSuite(TestThatScriptSourceIsWrittenToTestCaseDir),
        unittest.makeSuite(TestWhenInterpreterDoesNotExistThanExecuteShouldGiveHardError),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
