import os
import pathlib
import unittest

from shellcheck_lib.execution import environment_variables
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.execution.partial_execution import Configuration
from shellcheck_lib_test.execution.util import py_unit_test_case_with_file_output as with_file_output
from shellcheck_lib_test.execution.util.py_unit_test_case_with_file_output import \
    InternalInstructionThatWritesToStandardPhaseFile
from shellcheck_lib.execution import phases
from shellcheck_lib_test.execution.util import py_unit_test_case
from shellcheck_lib.test_case.instruction import common
from shellcheck_lib_test.execution.util import utils
from shellcheck_lib.test_case.sections.act import ActPhaseInstruction, PhaseEnvironmentForScriptGeneration

HOME_DIR_HEADER = 'Home Dir'
TEST_ROOT_DIR_HEADER = 'Test Root Dir'
CURRENT_DIR_HEADER = 'Current Dir'

EXIT_CODE = 5


class TestCaseDocument(py_unit_test_case.TestCaseWithCommonDefaultForSetupAssertCleanup):
    def _default_instructions_for_setup_assert_cleanup(self, phase: phases.Phase) -> list:
        return [
            InternalInstructionThatCreatesAStandardPhaseFileInTestRootContainingDirectoryPaths(phase)
        ]

    def _act_phase(self) -> list:
        return [
            self._next_instruction_line(ActPhaseInstructionThatPrintsPathsOnStdoutAndStderr())
        ]


def assertions(utc: unittest.TestCase,
               actual: py_unit_test_case.Result):
    utils.assert_is_file_with_contents(utc,
                                       actual.execution_directory_structure.result.exitcode_file,
                                       str(EXIT_CODE))
    utils.assert_is_file_with_contents(utc,
                                       actual.execution_directory_structure.result.std.stdout_file,
                                       expected_output_on('sys.stdout',
                                                          actual.partial_executor.configuration))
    utils.assert_is_file_with_contents(utc,
                                       actual.execution_directory_structure.result.std.stderr_file,
                                       expected_output_on('sys.stderr',
                                                          actual.partial_executor.configuration))

    file_name_from_py_cmd_list = [with_file_output.standard_phase_file_base_name(phase)
                                  for phase in [phases.SETUP, phases.ASSERT, phases.CLEANUP]]
    assert_files_in_test_root_that_contain_name_of_test_root_dir(
        utc,
        actual.partial_executor.execution_directory_structure,
        actual.partial_executor.global_environment,
        file_name_from_py_cmd_list)


def assert_files_in_test_root_that_contain_name_of_test_root_dir(
        utc: unittest.TestCase,
        eds: ExecutionDirectoryStructure,
        global_environment: common.GlobalEnvironmentForPostEdsPhase,
        file_name_from_py_cmd_list: list):
    expected_contents = utils.un_lines(py_cmd_file_lines(global_environment.eds.act_dir,
                                                         global_environment.home_directory,
                                                         global_environment.eds))
    for base_name in file_name_from_py_cmd_list:
        file_path = eds.act_dir / base_name
        file_name = str(file_path)
        utc.assertTrue(
            file_path.exists(),
            'py-cmd File should exist: ' + file_name)
        utc.assertTrue(
            file_path.is_file(),
            'py-cmd Should be a regular file: ' + file_name)
        with open(str(file_path)) as f:
            actual_contents = f.read()
            utc.assertEqual(expected_contents,
                            actual_contents,
                            'py-cmd Contents of py-cmd generated file ' + file_name)


def py_cmd_file_lines(cwd: pathlib.Path,
                      home_directory: pathlib.Path,
                      eds: ExecutionDirectoryStructure) -> list:
    def fmt(header: str, value: str):
        return '%-20s%s' % (header, value)

    return [fmt(CURRENT_DIR_HEADER, str(cwd)),
            fmt(HOME_DIR_HEADER, str(home_directory)),
            fmt(TEST_ROOT_DIR_HEADER, str(eds.act_dir))]


class InternalInstructionThatCreatesAStandardPhaseFileInTestRootContainingDirectoryPaths(
    InternalInstructionThatWritesToStandardPhaseFile):
    def __init__(self,
                 phase: phases.Phase):
        super().__init__(phase)

    def _file_lines(self, environment: common.GlobalEnvironmentForPostEdsPhase) -> list:
        return py_cmd_file_lines(
            pathlib.Path().resolve(),
            environment.home_directory,
            environment.eds)


class ActPhaseInstructionThatPrintsPathsOnStdoutAndStderr(ActPhaseInstruction):
    def __init__(self):
        super().__init__()

    def validate(self, global_environment: common.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             global_environment: common.GlobalEnvironmentForPostEdsPhase,
             phase_environment: PhaseEnvironmentForScriptGeneration) -> sh.SuccessOrHardError:
        statements = [
                         'import sys',
                         'import os',
                         'import pathlib',
                     ] + \
                     self.print_on('sys.stdout', global_environment) + \
                     self.print_on('sys.stderr', global_environment) + \
                     ['sys.exit(%d)' % EXIT_CODE]
        phase_environment.append.raw_script_statements(statements)
        return sh.new_sh_success()

    def print_on(self,
                 file_object: str,
                 global_environment: common.GlobalEnvironmentForPostEdsPhase) -> list:
        return [
            self.write_line(file_object, file_object),
            self.write_path_line(file_object, HOME_DIR_HEADER, global_environment.home_directory),
            self.write_path_line(file_object, TEST_ROOT_DIR_HEADER, global_environment.eds.act_dir),
            self.write_prefix_and_expr(file_object, CURRENT_DIR_HEADER, 'str(pathlib.Path().resolve())'),
            self.write_env_var(file_object, environment_variables.ENV_VAR_HOME),
            self.write_env_var(file_object, environment_variables.ENV_VAR_ACT),
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
        output_with_header(TEST_ROOT_DIR_HEADER, str(configuration.act_dir)),
        output_with_header(CURRENT_DIR_HEADER, str(configuration.act_dir)),

        output_with_header(environment_variables.ENV_VAR_HOME, str(configuration.home_dir)),
        output_with_header(environment_variables.ENV_VAR_ACT, str(configuration.act_dir)),
        ''
    ])


def output_with_header(header: str, value: str) -> str:
    return '%-20s%s' % (header, value)
