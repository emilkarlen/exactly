from shelltest.exec_abs_syn.instruction_result import new_success

__author__ = 'emil'

import os
import pathlib

from shelltest.exec_abs_syn.config import Configuration
from shelltest.execution import execution
from shelltest_test.execution.util import py_unit_test_case_with_file_output as with_file_output
from shelltest_test.execution.util.py_unit_test_case_with_file_output import \
    InternalInstructionThatWritesToStandardPhaseFile
from shelltest import phases
from shelltest_test.execution.util.py_unit_test_case import UnitTestCaseForPy3Language
from shelltest.exec_abs_syn import instructions
from shelltest_test.execution.util import utils


HOME_DIR_HEADER = 'Home Dir'
TEST_ROOT_DIR_HEADER = 'Test Root Dir'
CURRENT_DIR_HEADER = 'Current Dir'

EXIT_CODE = 5


class TestCase(UnitTestCaseForPy3Language):
    def _default_instructions_for_setup_assert_cleanup(self, phase: phases.Phase) -> list:
        return [
            InternalInstructionThatCreatesAStandardPhaseFileInTestRootContainingDirectoryPaths(phase)
        ]

    def _act_phase(self) -> list:
        return [
            self._next_instruction_line(ActPhaseInstructionThatPrintsPathsOnStdoutAndStderr())
        ]

    def _assertions(self):
        self.assert_is_regular_file_with_contents(self.eds.result.exitcode_file,
                                                  str(EXIT_CODE))
        self.assert_is_regular_file_with_contents(self.eds.result.std.stdout_file,
                                                  expected_output_on('sys.stdout',
                                                                     self.test_case_execution.configuration))
        self.assert_is_regular_file_with_contents(self.eds.result.std.stderr_file,
                                                  expected_output_on('sys.stderr',
                                                                     self.test_case_execution.configuration))

        file_name_from_py_cmd_list = [with_file_output.standard_phase_file_base_name(phase)
                                      for phase in [phases.SETUP, phases.ASSERT, phases.CLEANUP]]
        self.assert_files_in_test_root_that_contain_name_of_test_root_dir(
            self.test_case_execution.execution_directory_structure,
            self.test_case_execution.global_environment,
            file_name_from_py_cmd_list)

    def assert_files_in_test_root_that_contain_name_of_test_root_dir(
            self,
            eds: execution.ExecutionDirectoryStructure,
            global_environment: instructions.GlobalEnvironmentForNamedPhase,
            file_name_from_py_cmd_list: list):
        expected_contents = utils.un_lines(py_cmd_file_lines(global_environment.eds.test_root_dir,
                                                             global_environment))
        for base_name in file_name_from_py_cmd_list:
            file_path = eds.test_root_dir / base_name
            file_name = str(file_path)
            self.unittest_case.assertTrue(file_path.exists(),
                'py-cmd File should exist: ' + file_name)
            self.unittest_case.assertTrue(file_path.is_file(),
                'py-cmd Should be a regular file: ' + file_name)
            with open(str(file_path)) as f:
                actual_contents = f.read()
                self.unittest_case.assertEqual(expected_contents,
                                               actual_contents,
                                               'py-cmd Contents of py-cmd generated file ' + file_name)


def py_cmd_file_lines(cwd: pathlib.Path,
                      global_environment: instructions.GlobalEnvironmentForNamedPhase) -> list:
    def fmt(header: str, value: str):
        return '%-20s%s' % (header, value)

    return [fmt(CURRENT_DIR_HEADER, str(cwd)),
            fmt(HOME_DIR_HEADER, str(global_environment.home_directory)),
            fmt(TEST_ROOT_DIR_HEADER, str(global_environment.eds.test_root_dir))]


class InternalInstructionThatCreatesAStandardPhaseFileInTestRootContainingDirectoryPaths(
    InternalInstructionThatWritesToStandardPhaseFile):
    def __init__(self,
                 phase: phases.Phase):
        super().__init__(phase)

    def _file_lines(self, global_environment: instructions.GlobalEnvironmentForNamedPhase) -> list:
        return py_cmd_file_lines(
            pathlib.Path().resolve(),
            global_environment)


class ActPhaseInstructionThatPrintsPathsOnStdoutAndStderr(instructions.ActPhaseInstruction):
    def __init__(self):
        super().__init__()

    def update_phase_environment(self, phase_name: str,
                global_environment: instructions.GlobalEnvironmentForNamedPhase,
                phase_environment: instructions.PhaseEnvironmentForScriptGeneration) -> instructions.SuccessOrHardError:
        statements = [
                         'import sys',
                         'import os',
                         'import pathlib',
                     ] + \
                     self.print_on('sys.stdout', global_environment) + \
                     self.print_on('sys.stderr', global_environment) + \
                     ['sys.exit(%d)' % EXIT_CODE]
        phase_environment.append.raw_script_statements(statements)
        return new_success()

    def print_on(self,
                 file_object: str,
                 global_environment: instructions.GlobalEnvironmentForNamedPhase) -> list:
        return [
            self.write_line(file_object, file_object),
            self.write_path_line(file_object, HOME_DIR_HEADER, global_environment.home_directory),
            self.write_path_line(file_object, TEST_ROOT_DIR_HEADER, global_environment.eds.test_root_dir),
            self.write_prefix_and_expr(file_object, CURRENT_DIR_HEADER, 'str(pathlib.Path().resolve())'),
            self.write_env_var(file_object, execution.ENV_VAR_HOME),
            self.write_env_var(file_object, execution.ENV_VAR_TEST),
        ]

    @staticmethod
    def write_path_line(output_file: str,
                        line_prefix: str,
                        dir_path: pathlib.Path) -> str:
        return ActPhaseInstructionThatPrintsPathsOnStdoutAndStderr.write_prefix_and_expr(
            output_file,
            line_prefix,
            '\'' + str(dir_path) + '\'')

    @staticmethod
    def write_env_var(output_file: str,
                      var_name: str) -> str:
        return ActPhaseInstructionThatPrintsPathsOnStdoutAndStderr.write_prefix_and_expr(
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
