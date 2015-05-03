from shelltest.exec_abs_syn.instruction_result import new_success

__author__ = 'emil'

from shelltest_test.execution.util.py_unit_test_case import UnitTestCaseForPy3Language
from shelltest.exec_abs_syn import instructions


class TestCase(UnitTestCaseForPy3Language):
    """
    Checks that output to stdout, stderr and the exit code are saved in the correct locations.
    """

    INPUT_TMP_FILE = 'input.txt'

    EXPECTED_EXIT_CODE = 0
    TEXT_ON_STDIN = 'on stdin'
    EXPECTED_CONTENTS_OF_STDERR = ''

    def _setup_phase(self) -> list:
        return [
            self._next_instruction_line(PyCommandThatStoresStringInFileInCurrentDirectory2(self.INPUT_TMP_FILE,
                                                                                           self.TEXT_ON_STDIN))
        ]

    def _act_phase(self) -> list:
        return [
            self._next_instruction_line(InstructionThatSetsStdinFileName(self.INPUT_TMP_FILE)),
            self._next_instruction_line(StatementsThatCopiesStdinToStdout2())
        ]

    def _assertions(self):
        self.assert_is_regular_file_with_contents(self.eds.result.exitcode_file,
                                                  str(self.EXPECTED_EXIT_CODE))
        self.assert_is_regular_file_with_contents(self.eds.result.std.stdout_file,
                                                  self.TEXT_ON_STDIN)
        self.assert_is_regular_file_with_contents(self.eds.result.std.stderr_file,
                                                  self.EXPECTED_CONTENTS_OF_STDERR)


class PyCommandThatStoresStringInFileInCurrentDirectory2(instructions.SetupPhaseInstruction):
    def __init__(self,
                 file_base_name: str,
                 text_to_store: str):
        super().__init__()
        self.__file_base_name = file_base_name
        self.__text_to_store = text_to_store

    def execute(self, phase_name: str,
                global_environment: instructions.GlobalEnvironmentForNamedPhase,
                phase_environment: instructions.PhaseEnvironmentForInternalCommands):
        with open(self.__file_base_name, 'w') as f:
            f.write(self.__text_to_store)
        return new_success()


class StatementsThatCopiesStdinToStdout2(instructions.ActPhaseInstruction):
    def __init__(self):
        super().__init__()

    def update_phase_environment(self,
                phase_name: str,
                global_environment: instructions.GlobalEnvironmentForNamedPhase,
                phase_environment: instructions.PhaseEnvironmentForScriptGeneration):
        statements = [
            'import sys',
            'sys.stdout.write(sys.stdin.read())',
        ]
        return phase_environment.append.raw_script_statements(statements)


class InstructionThatSetsStdinFileName(instructions.ActPhaseInstruction):
    def __init__(self,
                 file_name: str):
        super().__init__()
        self.__file_name = file_name

    def update_phase_environment(self,
                phase_name: str,
                global_environment: instructions.GlobalEnvironmentForNamedPhase,
                phase_environment: instructions.PhaseEnvironmentForScriptGeneration):
        phase_environment.set_stdin_file(self.__file_name)