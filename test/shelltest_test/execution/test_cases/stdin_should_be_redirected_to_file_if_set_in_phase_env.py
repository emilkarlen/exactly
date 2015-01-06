__author__ = 'emil'

from shelltest import phases
from shelltest_test.execution.util.py_unit_test_case import UnitTestCaseForPyLanguage
from shelltest.exec_abs_syn import abs_syn_gen, script_stmt_gen, py_cmd_gen
from shelltest.exec_abs_syn.config import Configuration
from shelltest.phase_instr import line_source
from shelltest_test.execution.util import utils


class TestCase(UnitTestCaseForPyLanguage):
    """
    Checks that output to stdout, stderr and the exit code are saved in the correct locations.
    """

    INPUT_TMP_FILE = 'input.txt'

    EXPECTED_EXIT_CODE = 0
    TEXT_ON_STDIN = 'on stdin'
    EXPECTED_CONTENTS_OF_STDERR = ''

    def _phase_env_setup(self) -> abs_syn_gen.PhaseEnvironmentForPythonCommands:
        return abs_syn_gen.PhaseEnvironmentForPythonCommands(
            [PyCommandThatStoresStringInFileInCurrentDirectory(self._next_line(),
                                                               self.INPUT_TMP_FILE,
                                                               self.TEXT_ON_STDIN)]
        )

    def _phase_env_apply(self) -> abs_syn_gen.PhaseEnvironmentForScriptGeneration:
        return \
            abs_syn_gen.PhaseEnvironmentForScriptGeneration(
                [
                    StatementsThatCopiesStdinToStdout(self._next_line())
                ],
                stdin_file=self.INPUT_TMP_FILE
            )

    def _phase_env_for_py_cmd_phase(self, phase: phases.Phase) -> abs_syn_gen.PhaseEnvironmentForPythonCommands:
        return abs_syn_gen.PhaseEnvironmentForPythonCommands()

    def _assertions(self):
        utils.assert_is_file_with_contents(self.unittest_case,
                                           self.eds.result.exitcode_file,
                                           str(self.EXPECTED_EXIT_CODE))
        utils.assert_is_file_with_contents(self.unittest_case,
                                           self.eds.result.std.stdout_file,
                                           self.TEXT_ON_STDIN)
        utils.assert_is_file_with_contents(self.unittest_case,
                                           self.eds.result.std.stderr_file,
                                           self.EXPECTED_CONTENTS_OF_STDERR)


class PyCommandThatStoresStringInFileInCurrentDirectory(py_cmd_gen.PythonCommand):
    def __init__(self,
                 source_line: line_source.Line,
                 file_base_name: str,
                 text_to_store: str):
        super().__init__(source_line)
        self.__file_base_name = file_base_name
        self.__text_to_store = text_to_store

    def apply(self, configuration: Configuration):
        with open(self.__file_base_name, 'w') as f:
            f.write(self.__text_to_store)


class StatementsThatCopiesStdinToStdout(script_stmt_gen.StatementsGeneratorForInstruction):
    def __init__(self,
                 source_line: line_source.Line):
        super().__init__(source_line)

    def instruction_implementation(self,
                                   configuration: Configuration,
                                   script_language: script_stmt_gen.ScriptLanguage) -> list:
        statements = [
            'import sys',
            'sys.stdout.write(sys.stdin.read())',
        ]
        return script_language.raw_script_statements(statements)
