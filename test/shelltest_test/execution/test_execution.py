__author__ = 'emil'

import os
import pathlib
import tempfile
import unittest

from shelltest_test.execution.test_cases.execution_environment_variables import \
    TestEnvironmentVariablesShouldBeAccessibleInEveryPhase

from shelltest_test.execution.util.utils import Python3Language, assert_is_file_with_contents, un_lines
from shelltest_test.execution.util.py_unit_test_case_with_file_output import PyCommandThatWritesToStandardPhaseFile
from shelltest_test.execution.util import py_unit_test_case_with_file_output as with_file_output
from shelltest.phase_instr import line_source
from shelltest.exec_abs_syn import script_stmt_gen, abs_syn_gen
from shelltest.exec_abs_syn.abs_syn_gen import \
    new_test_case_phase_for_python_commands, \
    new_test_case_phase_for_script_statements
from shelltest.exec_abs_syn.config import Configuration
from shelltest.execution import execution
from shelltest import phases


HOME_DIR_HEADER = 'Home Dir'
TEST_ROOT_DIR_HEADER = 'Test Root Dir'
CURRENT_DIR_HEADER = 'Current Dir'

EXIT_CODE = 5


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


def py_cmd_file_lines(cwd: pathlib.Path, configuration: Configuration) -> list:
    def fmt(header: str, value: str):
        return '%-20s%s' % (header, value)

    return [fmt(CURRENT_DIR_HEADER, str(cwd)),
            fmt(HOME_DIR_HEADER, str(configuration.home_dir)),
            fmt(TEST_ROOT_DIR_HEADER, str(configuration.test_root_dir))]


class PyCommandThatCreatesAStandardPhaseFileInTestRootContainingDirectoryPaths(PyCommandThatWritesToStandardPhaseFile):
    def __init__(self,
                 source_line: line_source.Line,
                 file_base_name: str):
        super().__init__(source_line, file_base_name)

    def file_lines(self, configuration) -> list:
        return py_cmd_file_lines(pathlib.Path().resolve(), configuration)


def py_cmd_test_case_phase_that_creates_a_file_with_name_of_phase(phase: phases.Phase) -> abs_syn_gen.TestCasePhase:
    env = abs_syn_gen.PhaseEnvironmentForPythonCommands()
    env.append_command(
        PyCommandThatCreatesAStandardPhaseFileInTestRootContainingDirectoryPaths(
            line_source.Line(1, 'py-cmd: create file'),
            with_file_output.standard_phase_file_base_name(phase)))
    return new_test_case_phase_for_python_commands(phase,
                                                   env)


class Test(unittest.TestCase):
    def test_write_and_execute(self):
        # ARRANGE #
        home_dir_path = pathlib.Path().resolve()
        test_case = abs_syn_gen.TestCase(abs_syn_gen.GlobalEnvironmentForNamedPhase(str(home_dir_path)),
                                         [
                                             py_cmd_test_case_phase_that_creates_a_file_with_name_of_phase(
                                                 phases.SETUP),

                                             new_test_case_phase_for_script_statements(
                                                 phases.APPLY,
                                                 abs_syn_gen.PhaseEnvironmentForScriptGeneration(
                                                     [StatementsGeneratorThatPrintsPathsOnStdoutAndStderr()])),

                                             py_cmd_test_case_phase_that_creates_a_file_with_name_of_phase(
                                                 phases.ASSERT),

                                             py_cmd_test_case_phase_that_creates_a_file_with_name_of_phase(
                                                 phases.CLEANUP),
                                         ])
        # ACT #
        python3_language = Python3Language()
        file_name_from_py_cmd_list = [with_file_output.standard_phase_file_base_name(phase)
                                      for phase in [phases.SETUP, phases.ASSERT, phases.CLEANUP]]
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
            assert_is_file_with_contents(self,
                                         eds.result.exitcode_file,
                                         str(EXIT_CODE))
            assert_is_file_with_contents(self,
                                         eds.result.std.stdout_file,
                                         expected_output_on('sys.stdout',
                                                            test_case_execution.configuration))
            assert_is_file_with_contents(self,
                                         eds.result.std.stderr_file,
                                         expected_output_on('sys.stderr',
                                                            test_case_execution.configuration))
            self.assert_files_in_test_root_that_contain_name_of_test_root_dir(
                test_case_execution.execution_directory_structure,
                test_case_execution.configuration,
                file_name_from_py_cmd_list)

    def test_environment_variables_should_be_accessible_in_all_phases(self):
        TestEnvironmentVariablesShouldBeAccessibleInEveryPhase(self).execute()

    def test_test_root_dir_should_be_cwd_at_start_of_each_phase(self):
        pass  # TODO

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

    def assert_files_in_test_root_that_contain_name_of_test_root_dir(self,
                                                                     eds: execution.ExecutionDirectoryStructure,
                                                                     configuration: Configuration,
                                                                     file_name_from_py_cmd_list: list):
        expected_contents = un_lines(py_cmd_file_lines(configuration.test_root_dir, configuration))
        for base_name in file_name_from_py_cmd_list:
            file_path = eds.test_root_dir / base_name
            file_name = str(file_path)
            self.assertTrue(file_path.exists(),
                            'py-cmd File should exist: ' + file_name)
            self.assertTrue(file_path.is_file(),
                            'py-cmd Should be a regular file: ' + file_name)
            with open(str(file_path)) as f:
                actual_contents = f.read()
                self.assertEqual(expected_contents,
                                 actual_contents,
                                 'py-cmd Contents of py-cmd generated file ' + file_name)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(Test))
    return ret_val


if __name__ == '__main__':
    unittest.main()
