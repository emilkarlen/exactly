import os

__author__ = 'emil'

import subprocess
import pathlib

from shelltest import phase

from shelltest.execution.execution_directory_structure import construct_at, ExecutionDirectoryStructure
from shelltest.exec_abs_syn import script_stmt_gen, abs_syn_gen
from shelltest.exec_abs_syn.config import Configuration
from shelltest.execution import write_testcase_file
from shelltest import exception


ENV_VAR_HOME = 'SHELLTEST_HOME'
ENV_VAR_TEST = 'SHELLTEST_TESTROOT'


class TestCaseExecution:
    def __init__(self,
                 script_language: script_stmt_gen.ScriptLanguage,
                 test_case: abs_syn_gen.TestCase,
                 existing_execution_directory_root: str,
                 home_dir: pathlib.Path):
        self.__script_language = script_language
        self.__test_case = test_case
        self.__existing_execution_directory_root = existing_execution_directory_root
        self.__home_dir = home_dir
        self.__execution_directory_structure = None
        self.__configuration = None
        self.__script_file_path = None

    def write_and_execute(self):
        self.write()
        self.execute()

    def write(self):
        """
        Creates all necessary directories and files and executes the test case.
        """
        self.__execution_directory_structure = construct_at(self.__existing_execution_directory_root)
        self.__configuration = Configuration(self.__home_dir,
                                             self.__execution_directory_structure.test_root_dir)
        apply_phase = self.__test_case.lookup_phase(phase.APPLY)
        script_gen_env = apply_phase.phase_environment
        if not isinstance(script_gen_env,
                          abs_syn_gen.PhaseEnvironmentForScriptGeneration):
            raise ValueError('Environment for the "%s" phase is not a %s' %
                             (phase.APPLY.name, str(abs_syn_gen.PhaseEnvironmentForScriptGeneration)))
        self.__script_file_path = \
            write_testcase_file.write(self.__script_language,
                                      self.__execution_directory_structure,
                                      self.__configuration,
                                      phase.APPLY,
                                      script_gen_env.statements_generators)

    def execute(self):
        """
        Pre-condition: write has been executed.
        """
        cmd_and_args = self.script_language.command_and_args_for_executing_script_file(str(self.script_file_path))

        with open(str(self.execution_directory_structure.result.std.stdout_file), 'w') as f_stdout:
            with open(str(self.execution_directory_structure.result.std.stderr_file), 'w') as f_stderr:
                try:
                    os.environ[ENV_VAR_HOME] = str(self.home_dir)
                    os.environ[ENV_VAR_TEST] = str(self.execution_directory_structure.test_root_dir)
                    exitcode = subprocess.call(cmd_and_args,
                                               cwd=str(self.execution_directory_structure.test_root_dir),
                                               stdout=f_stdout,
                                               stderr=f_stderr)
                    self._store_exit_code(exitcode)
                except ValueError as ex:
                    msg = 'Error invoking subprocess.call: ' + str(ex)
                    raise exception.ImplementationError(msg)
                except OSError as ex:
                    msg = 'Error invoking subprocess.call: ' + str(ex)
                    raise exception.ImplementationError(msg)


    @property
    def script_language(self) -> script_stmt_gen.ScriptLanguage:
        return self.__script_language

    @property
    def test_case(self) -> abs_syn_gen.TestCase:
        return self.__test_case

    @property
    def home_dir(self) -> pathlib.Path:
        return self.__home_dir

    @property
    def execution_directory_structure(self) -> ExecutionDirectoryStructure:
        if not self.__execution_directory_structure:
            raise ValueError('execution_directory_structure')
        return self.__execution_directory_structure

    @property
    def script_file_path(self) -> pathlib.Path:
        if not self.__script_file_path:
            raise ValueError('script_file_path')
        return self.__script_file_path

    @property
    def configuration(self) -> Configuration:
        if not self.__configuration:
            raise ValueError('configuration')
        return self.__configuration

    def _store_exit_code(self, exitcode: int):
        with open(str(self.execution_directory_structure.result.exitcode_file), 'w') as f:
            f.write(str(exitcode))
