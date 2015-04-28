from shelltest.exec_abs_syn import instructions

__author__ = 'emil'

from shelltest import phases
from shelltest_test.execution.util.py_unit_test_case import UnitTestCaseForPyLanguage, UnitTestCaseForPyLanguage2
from shelltest.exec_abs_syn import abs_syn_gen, script_stmt_gen
from shelltest.exec_abs_syn.config import Configuration


class TestCase(UnitTestCaseForPyLanguage):
    """
    Checks that output to stdout, stderr and the exit code are saved in the correct locations.
    """

    TEXT_ON_STDOUT = 'on stdout'
    TEXT_ON_STDERR = 'on stderr'
    EXIT_CODE = 5

    def _phase_env_act(self) -> instructions.PhaseEnvironmentForScriptGeneration:
        return \
            instructions.PhaseEnvironmentForScriptGeneration([
                StatementsGeneratorThatPrintsPathsOnStdoutAndStderr(self.EXIT_CODE,
                                                                    self.TEXT_ON_STDOUT,
                                                                    self.TEXT_ON_STDERR)
            ])

    def _phase_env_for_py_cmd_phase(self, phase: phases.Phase) -> abs_syn_gen.PhaseEnvironmentForPythonCommands:
        return abs_syn_gen.PhaseEnvironmentForPythonCommands()

    def _assertions(self):
        self.assert_is_regular_file_with_contents(self.eds.result.exitcode_file,
                                                  str(self.EXIT_CODE))
        self.assert_is_regular_file_with_contents(self.eds.result.std.stdout_file,
                                                  self.TEXT_ON_STDOUT)
        self.assert_is_regular_file_with_contents(self.eds.result.std.stderr_file,
                                                  self.TEXT_ON_STDERR)


class TestCase2(UnitTestCaseForPyLanguage2):
    """
    Checks that output to stdout, stderr and the exit code are saved in the correct locations.
    """

    TEXT_ON_STDOUT = 'on stdout'
    TEXT_ON_STDERR = 'on stderr'
    EXIT_CODE = 5

    def _act_phase(self) -> list:
        return [
            self._next_instruction_line(
                StatementsGeneratorThatPrintsPathsOnStdoutAndStderr2(self.EXIT_CODE,
                                                                     self.TEXT_ON_STDOUT,
                                                                     self.TEXT_ON_STDERR))
        ]

    def _assertions(self):
        self.assert_is_regular_file_with_contents(self.eds.result.exitcode_file,
                                                  str(self.EXIT_CODE))
        self.assert_is_regular_file_with_contents(self.eds.result.std.stdout_file,
                                                  self.TEXT_ON_STDOUT)
        self.assert_is_regular_file_with_contents(self.eds.result.std.stderr_file,
                                                  self.TEXT_ON_STDERR)


class StatementsGeneratorThatPrintsPathsOnStdoutAndStderr(script_stmt_gen.StatementsGeneratorForInstruction):
    def __init__(self,
                 exit_code: int,
                 text_on_stdout: str,
                 text_on_stderr: str):
        super().__init__()
        self.__text_on_stdout = text_on_stdout
        self.__text_on_stderr = text_on_stderr
        self.__exit_code = exit_code

    def instruction_implementation(self,
                                   configuration: Configuration,
                                   script_language: script_stmt_gen.ScriptLanguage) -> list:
        statements = [
            'import sys',
            self.write_on('sys.stdout', self.__text_on_stdout),
            self.write_on('sys.stderr', self.__text_on_stderr),
            'sys.exit(%d)' % self.__exit_code
        ]
        return script_language.raw_script_statements(statements)

    @staticmethod
    def write_on(output_file: str,
                 text: str) -> str:
        return "%s.write('%s')" % (output_file, text)


class StatementsGeneratorThatPrintsPathsOnStdoutAndStderr2(instructions.ActPhaseInstruction):
    def __init__(self,
                 exit_code: int,
                 text_on_stdout: str,
                 text_on_stderr: str):
        super().__init__()
        self.__text_on_stdout = text_on_stdout
        self.__text_on_stderr = text_on_stderr
        self.__exit_code = exit_code

    def execute(self, phase_name: str,
                global_environment: instructions.GlobalEnvironmentForNamedPhase,
                phase_environment: instructions.PhaseEnvironmentForScriptGeneration):
        statements = [
            'import sys',
            self.write_on('sys.stdout', self.__text_on_stdout),
            self.write_on('sys.stderr', self.__text_on_stderr),
            'sys.exit(%d)' % self.__exit_code
        ]
        return phase_environment.append.raw_script_statements(statements)

    @staticmethod
    def write_on(output_file: str,
                 text: str) -> str:
        return "%s.write('%s')" % (output_file, text)
