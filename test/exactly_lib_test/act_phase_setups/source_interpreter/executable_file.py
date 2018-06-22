import pathlib
import unittest
from contextlib import contextmanager

from exactly_lib.act_phase_setups.source_interpreter import executable_file as sut, python3
from exactly_lib.act_phase_setups.source_interpreter.source_file_management import SourceFileManager, \
    SourceInterpreterSetup
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.util.process_execution.command import ProgramAndArguments
from exactly_lib.util.string import lines_content
from exactly_lib_test.act_phase_setups.source_interpreter import common_tests
from exactly_lib_test.act_phase_setups.test_resources.act_phase_execution import Arrangement, Expectation, \
    check_execution
from exactly_lib_test.act_phase_setups.test_resources.act_source_and_executor import \
    Configuration, suite_for_execution, TestCaseSourceSetup
from exactly_lib_test.execution.test_resources import eh_assertions
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    test_case_dir_contains_exactly
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.util.test_resources import py_program


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_execution(TheConfiguration()),
        unittest.makeSuite(TestThatScriptSourceIsWrittenToTestCaseDir),
        unittest.makeSuite(TestWhenInterpreterDoesNotExistThanExecuteShouldGiveHardError),

        common_tests.suite_for(sut.Constructor(python3.source_interpreter_setup()),
                               is_shell=False),
    ])


class TheConfiguration(Configuration):
    def __init__(self):
        self.setup = sut.new_for_source_interpreter_setup(python3.source_interpreter_setup())
        super().__init__(self.setup.source_and_executor_constructor)

    @contextmanager
    def program_that_copes_stdin_to_stdout(self, hds: HomeDirectoryStructure) -> list:
        yield _instructions_for(py_program.copy_stdin_to_stdout())

    @contextmanager
    def program_that_prints_to_stderr(self,
                                      hds: HomeDirectoryStructure,
                                      string_to_print: str) -> list:
        yield _instructions_for(py_program.write_string_to_stderr(string_to_print))

    @contextmanager
    def program_that_prints_to_stdout(self,
                                      hds: HomeDirectoryStructure,
                                      string_to_print: str) -> list:
        yield _instructions_for(py_program.write_string_to_stdout(string_to_print))

    @contextmanager
    def program_that_exits_with_code(self,
                                     hds: HomeDirectoryStructure,
                                     exit_code: int) -> list:
        yield _instructions_for(py_program.exit_with_code(exit_code))

    @contextmanager
    def program_that_prints_cwd_without_new_line_to_stdout(self, hds: HomeDirectoryStructure) -> list:
        yield _instructions_for(py_program.write_cwd_to_stdout())

    @contextmanager
    def program_that_prints_value_of_environment_variable_to_stdout(self,
                                                                    hds: HomeDirectoryStructure,
                                                                    var_name: str) -> list:
        yield _instructions_for(py_program.write_value_of_environment_variable_to_stdout(var_name))

    @contextmanager
    def program_that_sleeps_at_least(self, number_of_seconds: int) -> TestCaseSourceSetup:
        yield TestCaseSourceSetup(act_phase_instructions=_instructions_for(
            py_program.program_that_sleeps_at_least_and_then_exists_with_zero_exit_status(number_of_seconds)))


def _instructions_for(statements: list) -> list:
    return list(map(lambda stmt: instr([stmt]), statements))


class TestWhenInterpreterDoesNotExistThanExecuteShouldGiveHardError(unittest.TestCase):
    def runTest(self):
        language_setup = SourceInterpreterSetup(_SourceFileManagerWithNonExistingInterpreter())
        act_phase_setup = sut.new_for_source_interpreter_setup(language_setup)
        empty_source = []
        check_execution(self,
                        act_phase_setup.source_and_executor_constructor,
                        empty_source,
                        Arrangement(),
                        Expectation(
                            result_of_execute=eh_assertions.is_hard_error))


class TestThatScriptSourceIsWrittenToTestCaseDir(unittest.TestCase):
    def runTest(self):
        language_setup = SourceInterpreterSetup(_SourceFileManagerWithNonExistingInterpreter())
        act_phase_setup = sut.new_for_source_interpreter_setup(language_setup)
        source = [instr(['print(1)'])]
        expected_file_name = language_setup.base_name_from_stem(
            sut.ActSourceFileNameGeneratorForSourceInterpreterSetup.FILE_NAME_STEM)
        exit_code_or_hard_error = check_execution(
            self,
            act_phase_setup.source_and_executor_constructor,
            source,
            Arrangement(),
            Expectation(
                result_of_execute=eh_assertions.is_hard_error,
                side_effects_on_files_after_execute=test_case_dir_contains_exactly(DirContents([
                    File(expected_file_name,
                         lines_content(['print(1)']))
                ]))))
        self.assertTrue(exit_code_or_hard_error.is_hard_error,
                        'Expecting a HARD ERROR')


class _SourceFileManagerWithNonExistingInterpreter(SourceFileManager):
    def command_and_args_for_executing_script_file(self, script_file_name: str) -> ProgramAndArguments:
        interpreter_path = pathlib.Path().cwd().resolve() / 'non-existing-interpreter'
        return ProgramAndArguments(str(interpreter_path),
                                   [script_file_name])

    def base_name_from_stem(self, stem: str) -> str:
        return stem + '.src'


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
