from shelltest.exec_abs_syn import instructions
from shelltest.phase_instr.model import PhaseContents, PhaseContentElement

__author__ = 'emil'

import tempfile
import os
import subprocess
import pathlib

from shelltest import phases
from shelltest.exec_abs_syn import py_cmd_gen
from shelltest.exec_abs_syn import script_stmt_gen, abs_syn_gen
from shelltest.exec_abs_syn.config import Configuration
from shelltest import exception
from . import write_testcase_file
from .execution_directory_structure import construct_at, ExecutionDirectoryStructure


ENV_VAR_HOME = 'SHELLTEST_HOME'
ENV_VAR_TEST = 'SHELLTEST_TESTROOT'

ALL_ENV_VARS = [ENV_VAR_HOME, ENV_VAR_TEST]


class TestCaseExecution:
    """
    Executes a given Test Case in an existing
    Execution Directory Root.
    """

    def __init__(self,
                 script_language: script_stmt_gen.ScriptLanguage,
                 test_case: abs_syn_gen.TestCase,
                 execution_directory_structure: ExecutionDirectoryStructure,
                 configuration: Configuration):
        self.__script_language = script_language
        self.__test_case = test_case
        self.__execution_directory_structure = execution_directory_structure
        self.__configuration = configuration
        self.__script_file_path = None

    def write_and_execute(self):
        self.write()
        self.execute()

    def write(self):
        """
        Creates all necessary directories and files.
        """
        act_phase = self.__test_case.lookup_phase(phases.ACT)
        script_gen_env = act_phase.phase_environment
        if not isinstance(script_gen_env,
                          instructions.PhaseEnvironmentForScriptGeneration):
            raise ValueError('Environment for the "%s" phase is not a %s' %
                             (phases.ACT.name, str(instructions.PhaseEnvironmentForScriptGeneration)))
        self.__script_file_path = \
            write_testcase_file.write(self.__script_language,
                                      self.__execution_directory_structure,
                                      self.__configuration,
                                      phases.ACT,
                                      script_gen_env.statements_generators)

    def execute(self):
        """
        Pre-condition: write has been executed.
        """
        os.environ[ENV_VAR_HOME] = str(self.configuration.home_dir)
        os.environ[ENV_VAR_TEST] = str(self.execution_directory_structure.test_root_dir)
        for test_case_phase in self.test_case.phase_list:
            if test_case_phase.phase == phases.ACT:
                self._execute_act(test_case_phase.phase_environment)
                continue
            phase_env = test_case_phase.phase_environment
            if isinstance(phase_env, abs_syn_gen.PhaseEnvironmentForPythonCommands):
                self._execute_py_commands_in_test_root(phase_env)

    @property
    def script_language(self) -> script_stmt_gen.ScriptLanguage:
        return self.__script_language

    @property
    def test_case(self) -> abs_syn_gen.TestCase:
        return self.__test_case

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

    def _execute_py_commands_in_test_root(self,
                                          phase_env: abs_syn_gen.PhaseEnvironmentForPythonCommands):
        os.chdir(str(self.execution_directory_structure.test_root_dir))
        for command in phase_env.commands:
            assert isinstance(command, py_cmd_gen.PythonCommand)
            command.apply(self.configuration)

    def _execute_act(self, phase_env: instructions.PhaseEnvironmentForScriptGeneration):
        """
        Pre-condition: write has been executed.
        """
        if phase_env.stdin_file_name:
            try:
                f_stdin = open(phase_env.stdin_file_name)
                self._execute_apply_with_stdin_file(f_stdin)
            finally:
                f_stdin.close()
        else:
            self._execute_apply_with_stdin_file(subprocess.DEVNULL)

    def _execute_apply_with_stdin_file(self, f_stdin):
        """
        Pre-condition: write has been executed.
        """
        cmd_and_args = self.script_language.command_and_args_for_executing_script_file(str(self.script_file_path))

        with open(str(self.execution_directory_structure.result.std.stdout_file), 'w') as f_stdout:
            with open(str(self.execution_directory_structure.result.std.stderr_file), 'w') as f_stderr:
                try:
                    exitcode = subprocess.call(cmd_and_args,
                                               cwd=str(self.execution_directory_structure.test_root_dir),
                                               stdin=f_stdin,
                                               stdout=f_stdout,
                                               stderr=f_stderr)
                    self._store_exit_code(exitcode)
                except ValueError as ex:
                    msg = 'Error invoking subprocess.call: ' + str(ex)
                    raise exception.ImplementationError(msg)
                except OSError as ex:
                    msg = 'Error invoking subprocess.call: ' + str(ex)
                    raise exception.ImplementationError(msg)


class TestCaseExecution2:
    """
    Executes a given Test Case in an existing
    Execution Directory Root.
    """

    def __init__(self,
                 global_environment: instructions.GlobalEnvironmentForNamedPhase,
                 execution_directory_structure: ExecutionDirectoryStructure,
                 configuration: Configuration,
                 act_env_after_execution: instructions.PhaseEnvironmentForScriptGeneration,
                 setup_phase: PhaseContents,
                 assert_phase: PhaseContents,
                 cleanup_phase: PhaseContents):
        self.__global_environment = global_environment
        self.__act_env_after_execution = act_env_after_execution
        self.__file_management = act_env_after_execution.script_file_management
        self.__setup_phase = setup_phase
        self.__assert_phase = assert_phase
        self.__cleanup_phase = cleanup_phase
        self.__execution_directory_structure = execution_directory_structure
        self.__configuration = configuration
        self.__script_file_path = None

    def write_and_execute(self):
        self.write_and_store_script_file_path()
        self.execute()

    def write_and_store_script_file_path(self):
        script_source = self.__act_env_after_execution.final_script_source
        base_name = self.__file_management.base_name_from_stem(phases.ACT.name)
        file_path = self.__execution_directory_structure.test_case_dir / base_name
        with open(str(file_path), 'w') as f:
            f.write(script_source)
        self.__script_file_path = file_path

    def execute(self):
        """
        Pre-condition: write has been executed.
        """
        # TODO Köra det här i sub-process?
        # Tror det behövs för att undvika att sätta omgivningen mm, o därmed
        # påverka huvudprocessen.
        os.environ[ENV_VAR_HOME] = str(self.configuration.home_dir)
        os.environ[ENV_VAR_TEST] = str(self.execution_directory_structure.test_root_dir)
        phase_env = instructions.PhaseEnvironmentForInternalCommands()
        self.__execute_internal_instructions(phases.SETUP, self.__setup_phase, phase_env)
        self.__run_act_script()
        self.__execute_internal_instructions(phases.ASSERT, self.__assert_phase, phase_env)
        self.__execute_internal_instructions(phases.CLEANUP, self.__cleanup_phase, phase_env)

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

    def __execute_internal_instructions(self,
                                        phase: phases.Phase,
                                        phase_contents: PhaseContents,
                                        phase_env: instructions.PhaseEnvironmentForInternalCommands):
        os.chdir(str(self.execution_directory_structure.test_root_dir))
        for element in phase_contents.elements:
            assert isinstance(element, instructions.InternalInstruction)
            element.execute(phase.name,
                            self.__global_environment,
                            phase_env)

    def _execute_py_commands_in_test_root(self,
                                          phase_env: abs_syn_gen.PhaseEnvironmentForPythonCommands):
        os.chdir(str(self.execution_directory_structure.test_root_dir))
        for command in phase_env.commands:
            assert isinstance(command, py_cmd_gen.PythonCommand)
            command.apply(self.configuration)

    def __run_act_script(self):
        """
        Pre-condition: write has been executed.
        """
        if self.__act_env_after_execution.stdin_file_name:
            try:
                f_stdin = open(self.__act_env_after_execution.stdin_file_name)
                self._run_act_script_with_stdin_file(f_stdin)
            finally:
                f_stdin.close()
        else:
            self._run_act_script_with_stdin_file(subprocess.DEVNULL)

    def _run_act_script_with_stdin_file(self, f_stdin):
        """
        Pre-condition: write has been executed.
        """
        cmd_and_args = self.__file_management.command_and_args_for_executing_script_file(str(self.script_file_path))

        with open(str(self.execution_directory_structure.result.std.stdout_file), 'w') as f_stdout:
            with open(str(self.execution_directory_structure.result.std.stderr_file), 'w') as f_stderr:
                try:
                    exitcode = subprocess.call(cmd_and_args,
                                               cwd=str(self.execution_directory_structure.test_root_dir),
                                               stdin=f_stdin,
                                               stdout=f_stdout,
                                               stderr=f_stderr)
                    self._store_exit_code(exitcode)
                except ValueError as ex:
                    msg = 'Error executing act phase as subprocess: ' + str(ex)
                    raise exception.ImplementationError(msg)
                except OSError as ex:
                    msg = 'Error executing act phase as subprocess: ' + str(ex)
                    raise exception.ImplementationError(msg)


def execute_test_case_in_execution_directory(script_language: script_stmt_gen.ScriptLanguage,
                                             test_case: abs_syn_gen.TestCase,
                                             home_dir_path: pathlib.Path,
                                             execution_directory_root_name_prefix: str,
                                             is_keep_execution_directory_root: bool) -> TestCaseExecution:
    """
    Takes care of construction of the Execution Directory Structure, including
    the root directory, and executes a given Test Case in this directory.

    Preserves Current Working Directory.

    Perhaps the test case should be executed in a sub process, so that
    Environment Variables and Current Working Directory of the process that executes
    shelltest is not modified.

    The responsibility of this method is not the most natural!!
    Please refactor if a more natural responsibility comes up!
    """

    def with_existing_root(exec_dir_structure_root: str) -> TestCaseExecution:
        cwd_before = os.getcwd()
        execution_directory_structure = construct_at(exec_dir_structure_root)
        configuration = Configuration(home_dir_path,
                                      execution_directory_structure.test_root_dir)
        test_case_execution = TestCaseExecution(script_language,
                                                test_case,
                                                execution_directory_structure,
                                                configuration)
        try:
            test_case_execution.write_and_execute()
        finally:
            os.chdir(cwd_before)
        return test_case_execution

    if is_keep_execution_directory_root:
        tmp_exec_dir_structure_root = tempfile.mkdtemp(prefix=execution_directory_root_name_prefix)
        return with_existing_root(tmp_exec_dir_structure_root)
    else:
        with tempfile.TemporaryDirectory(prefix=execution_directory_root_name_prefix) as tmp_exec_dir_structure_root:
            return with_existing_root(tmp_exec_dir_structure_root)


def __execute_act_phase(global_environment: instructions.GlobalEnvironmentForNamedPhase,
                        act_phase: PhaseContents,
                        act_environment: instructions.PhaseEnvironmentForScriptGeneration):
    """
    Accumulates the script source by executing all instructions, and adding
    comments from the test case file.

    :param act_environment: Post-condition: Contains the accumulated script source.
    """
    for element in act_phase.elements:
        assert isinstance(element, PhaseContentElement)
        if element.is_comment:
            act_environment.append.comment_line(element.source_line.text)
        else:
            act_environment.append.source_line_header(element.source_line)
            executor = element.executor
            assert isinstance(executor, instructions.ActPhaseInstruction)
            executor.execute(phases.ACT.name,
                             global_environment,
                             act_environment)


def execute_test_case_in_execution_directory2(script_file_management: script_stmt_gen.ScriptFileManager,
                                              script_source_writer: script_stmt_gen.ScriptSourceWriter,
                                              test_case: abs_syn_gen.TestCase2,
                                              home_dir_path: pathlib.Path,
                                              execution_directory_root_name_prefix: str,
                                              is_keep_execution_directory_root: bool) -> TestCaseExecution2:
    """
    Takes care of construction of the Execution Directory Structure, including
    the root directory, and executes a given Test Case in this directory.

    Preserves Current Working Directory.

    Perhaps the test case should be executed in a sub process, so that
    Environment Variables and Current Working Directory of the process that executes
    shelltest is not modified.

    The responsibility of this method is not the most natural!!
    Please refactor if a more natural responsibility evolves!
    """

    def with_existing_root(exec_dir_structure_root: str,
                           global_environment: instructions.GlobalEnvironmentForNamedPhase,
                           environment_after_execution: instructions.PhaseEnvironmentForScriptGeneration) \
            -> TestCaseExecution2:
        cwd_before = os.getcwd()
        execution_directory_structure = construct_at(exec_dir_structure_root)
        configuration = Configuration(home_dir_path,
                                      execution_directory_structure.test_root_dir)

        test_case_execution = TestCaseExecution2(global_environment,
                                                 execution_directory_structure,
                                                 configuration,
                                                 environment_after_execution,
                                                 test_case.setup_phase,
                                                 test_case.assert_phase,
                                                 test_case.cleanup_phase)
        try:
            test_case_execution.write_and_execute()
        finally:
            os.chdir(cwd_before)
        return test_case_execution

    global_environment = instructions.GlobalEnvironmentForNamedPhase(home_dir_path)
    act_environment = instructions.PhaseEnvironmentForScriptGeneration(script_file_management,
                                                                       script_source_writer)
    __execute_act_phase(global_environment, test_case.act_phase, act_environment)
    if is_keep_execution_directory_root:
        tmp_exec_dir_structure_root = tempfile.mkdtemp(prefix=execution_directory_root_name_prefix)
        return with_existing_root(tmp_exec_dir_structure_root,
                                  global_environment,
                                  act_environment)
    else:
        with tempfile.TemporaryDirectory(prefix=execution_directory_root_name_prefix) as tmp_exec_dir_structure_root:
            return with_existing_root(tmp_exec_dir_structure_root,
                                      global_environment,
                                      act_environment)
