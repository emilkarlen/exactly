import pathlib

__author__ = 'emil'

import os
from shelltest.execution import execution

from shelltest import phases
from shelltest_test.execution.util.py_unit_test_case import UnitTestCaseForPyLanguage
from shelltest.exec_abs_syn import abs_syn_gen, script_stmt_gen
from shelltest.exec_abs_syn.config import Configuration
from shelltest.phase_instr import line_source

from shelltest_test.execution.util import utils

HOME_DIR_HEADER = 'Home Dir'
TEST_ROOT_DIR_HEADER = 'Test Root Dir'
CURRENT_DIR_HEADER = 'Current Dir'

EXIT_CODE = 5


class TestCase(UnitTestCaseForPyLanguage):
    """
    Checks that output to stdout, stderr and the exit code are saved in the correct locations.
    """

    def _phase_env_apply(self) -> abs_syn_gen.PhaseEnvironmentForScriptGeneration:
        return \
            abs_syn_gen.PhaseEnvironmentForScriptGeneration([
                StatementsGeneratorThatPrintsPathsOnStdoutAndStderr()
            ])

    def _phase_env_for_py_cmd_phase(self, phase: phases.Phase) -> abs_syn_gen.PhaseEnvironmentForPythonCommands:
        return abs_syn_gen.PhaseEnvironmentForPythonCommands()

    def _assertions(self):
        utils.assert_is_file_with_contents(self.unittest_case,
                                           self.eds.result.exitcode_file,
                                           str(EXIT_CODE))
        utils.assert_is_file_with_contents(self.unittest_case,
                                           self.eds.result.std.stdout_file,
                                           expected_output_on('sys.stdout',
                                                              self.test_case_execution.configuration))
        utils.assert_is_file_with_contents(self.unittest_case,
                                           self.eds.result.std.stderr_file,
                                           expected_output_on('sys.stderr',
                                                              self.test_case_execution.configuration))


class StatementsGeneratorThatPrintsPathsOnStdoutAndStderr(script_stmt_gen.StatementsGeneratorForInstruction):
    def __init__(self):
        super().__init__(line_source.Line(1, 'one'))

    def instruction_implementation(self,
                                   configuration: Configuration,
                                   script_language: script_stmt_gen.ScriptLanguage) -> list:
        statements = [
                         'import sys',
                         'import os',
                         'import pathlib',
                     ] + \
                     self.print_on('sys.stdout', configuration) + \
                     self.print_on('sys.stderr', configuration) + \
                     ['sys.exit(%d)' % EXIT_CODE]

        return script_language.raw_script_statements(statements)

    def print_on(self,
                 file_object: str,
                 configuration: Configuration) -> list:
        return [
            self.write_line(file_object, file_object),
            self.write_path_line(file_object, HOME_DIR_HEADER, configuration.home_dir),
            self.write_path_line(file_object, TEST_ROOT_DIR_HEADER, configuration.test_root_dir),
            self.write_prefix_and_expr(file_object, CURRENT_DIR_HEADER, 'str(pathlib.Path().resolve())'),
            self.write_env_var(file_object, execution.ENV_VAR_HOME),
            self.write_env_var(file_object, execution.ENV_VAR_TEST),
        ]

    @staticmethod
    def write_path_line(output_file: str,
                        line_prefix: str,
                        dir_path: pathlib.Path) -> str:
        return StatementsGeneratorThatPrintsPathsOnStdoutAndStderr.write_prefix_and_expr(
            output_file,
            line_prefix,
            '\'' + str(dir_path) + '\'')

    @staticmethod
    def write_env_var(output_file: str,
                      var_name: str) -> str:
        return StatementsGeneratorThatPrintsPathsOnStdoutAndStderr.write_prefix_and_expr(
            output_file,
            var_name,
            'os.environ[\'%s\']' % var_name)

    @staticmethod
    def write_prefix_and_expr(output_file: str,
                              prefix: str,
                              expr: str) -> str:
        return 'print(\'%-20s\' + %s, file=%s)' % (prefix, expr, output_file)

    @staticmethod
    def write_line(output_file: str,
                   line: str) -> str:
        return 'print(\'%s\', file=%s)' % (line, output_file)


def expected_output_on(file_object: str,
                       configuration: Configuration) -> str:
    return os.linesep.join([
        file_object,

        output_with_header(HOME_DIR_HEADER, str(configuration.home_dir)),
        output_with_header(TEST_ROOT_DIR_HEADER, str(configuration.test_root_dir)),
        output_with_header(CURRENT_DIR_HEADER, str(configuration.test_root_dir)),

        output_with_header(execution.ENV_VAR_HOME, str(configuration.home_dir)),
        output_with_header(execution.ENV_VAR_TEST, str(configuration.test_root_dir)),
        ''
    ])


def output_with_header(header: str, value: str) -> str:
    return '%-20s%s' % (header, value)
