import os
import pathlib

__author__ = 'emil'

import tempfile
import unittest

from shelltest.phase_instr import line_source
from shelltest.exec_abs_syn import script_stmt_gen, abs_syn_gen
from shelltest.exec_abs_syn.abs_syn_gen import \
    new_test_case_phase_for_python_commands, \
    new_test_case_phase_for_script_statements
from shelltest.exec_abs_syn.config import Configuration
from shelltest.execution import execution
from shelltest import phase


HOME_DIR_HEADER = 'Home Dir'
TEST_ROOT_DIR_HEADER = 'Test Root Dir'
CURRENT_DIR_HEADER = 'Current Dir'

EXIT_CODE = 5


class Python3Language(script_stmt_gen.ScriptLanguage):
    def command_and_args_for_executing_script_file(self, script_file_name: str) -> list:
        return ['python3', script_file_name]

    def base_name_from_stem(self, stem: str):
        return stem + '.py'

    def comment_line(self, comment: str) -> list:
        return ['# ' + comment]

    def raw_script_statement(self, statement: str) -> list:
        return [statement]


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


def output_with_header(header: str, value: str) -> str:
    return '%-20s%s' % (header, value)


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


def empty_py_cmd_test_case_phase(ph: phase.Phase) -> abs_syn_gen.TestCasePhase:
    return new_test_case_phase_for_python_commands(ph,
                                                   abs_syn_gen.PhaseEnvironmentForPythonCommands())


class Test(unittest.TestCase):
    def test_write_and_execute(self):
        # ARRANGE #
        python3_language = Python3Language()
        printer_statement = StatementsGeneratorThatPrintsPathsOnStdoutAndStderr()
        home_dir_path = pathlib.Path().resolve()
        phase_env_for_assert = abs_syn_gen.PhaseEnvironmentForScriptGeneration()
        phase_env_for_assert.append_statement(printer_statement)
        test_case = abs_syn_gen.TestCase(abs_syn_gen.GlobalEnvironmentForNamedPhase(str(home_dir_path)),
                                         [
                                             empty_py_cmd_test_case_phase(phase.SETUP),
                                             new_test_case_phase_for_script_statements(phase.APPLY,
                                                                                       phase_env_for_assert),
                                             empty_py_cmd_test_case_phase(phase.ASSERT),
                                             empty_py_cmd_test_case_phase(phase.CLEANUP),
                                         ])
        # ACT #
        with tempfile.TemporaryDirectory(prefix='shelltest-test-') as tmp_exec_dir_structure_root:
            # tmp_exec_dir_structure_root = tempfile.mkdtemp(prefix='shelltest-')
            # print(tmp_exec_dir_structure_root)

            test_case_execution = execution.TestCaseExecution(python3_language,
                                                              test_case,
                                                              tmp_exec_dir_structure_root,
                                                              home_dir_path)
            test_case_execution.write_and_execute()
            # ASSERT #
            eds = test_case_execution.execution_directory_structure
            self.assert_is_file_with_contents(eds.result.exitcode_file,
                                              str(EXIT_CODE))
            self.assert_is_file_with_contents(eds.result.std.stdout_file,
                                              expected_output_on('sys.stdout',
                                                                 test_case_execution.configuration))
            self.assert_is_file_with_contents(eds.result.std.stderr_file,
                                              expected_output_on('sys.stderr',
                                                                 test_case_execution.configuration))

    def assert_is_file_with_contents(self,
                                     file_path: pathlib.Path,
                                     expected_content: str):
        file_name = str(file_path)
        self.assertTrue(file_path.exists(),
                        'File should exist: ' + file_name)
        self.assertTrue(file_path.is_file(),
                        'Should be a regular file: ' + file_name)
        f = open(str(file_path))
        actual_contents = f.read()
        f.close()
        self.assertEqual(expected_content,
                         actual_contents,
                         'Contents of ' + file_name)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(Test))
    return ret_val


if __name__ == '__main__':
    unittest.main()
