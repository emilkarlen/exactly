__author__ = 'emil'

import tempfile
import os
import subprocess
import pathlib

from shelltest.execution.phase_step import ACT_script_generation
from shelltest.execution.phase_step_executor import ElementHeaderExecutor
from shelltest.phase_instr import line_source
from shelltest.execution import phase_step_executors
from shelltest.execution.single_instruction_executor import ControlledInstructionExecutor
from shelltest.exec_abs_syn import instructions
from shelltest.phase_instr.model import PhaseContents
from shelltest import phases
from shelltest.exec_abs_syn import script_stmt_gen, abs_syn_gen
from shelltest.exec_abs_syn.config import Configuration
from shelltest import exception
from .execution_directory_structure import construct_at, ExecutionDirectoryStructure
from .result import PartialResult, PartialResultStatus
from . import result
from . import phase_step_executor


ENV_VAR_HOME = 'SHELLTEST_HOME'
ENV_VAR_TEST = 'SHELLTEST_TESTROOT'
ENV_VAR_TMP = 'SHELLTEST_TMP'

ALL_ENV_VARS = [ENV_VAR_HOME,
                ENV_VAR_TEST,
                ENV_VAR_TMP]


class _Executor:
    def __init__(self,
                 global_environment: instructions.GlobalEnvironmentForNamedPhase,
                 execution_directory_structure: ExecutionDirectoryStructure,
                 configuration: Configuration,
                 act_env_before_execution: instructions.PhaseEnvironmentForScriptGeneration,
                 setup_phase: PhaseContents,
                 act_phase: PhaseContents,
                 assert_phase: PhaseContents,
                 cleanup_phase: PhaseContents):
        self.__global_environment = global_environment
        self.__act_env_before_execution = act_env_before_execution
        self.__file_management = act_env_before_execution.script_file_management
        self.__setup_phase = setup_phase
        self.__act_phase = act_phase
        self.__assert_phase = assert_phase
        self.__cleanup_phase = cleanup_phase
        self.__execution_directory_structure = execution_directory_structure
        self.__configuration = configuration
        self.__script_file_path = None
        self.__partial_result = None

    def execute(self):
        """
        Pre-condition: write has been executed.
        """
        # TODO Köra det här i sub-process?
        # Tror det behövs för att undvika att sätta omgivningen mm, o därmed
        # påverka huvudprocessen.
        self.__set_environment_variables()
        phase_env = instructions.PhaseEnvironmentForInternalCommands()
        res = self.__run_setup(phase_env)
        if res.status is not PartialResultStatus.PASS:
            self.__partial_result = res
            return
        res = self.__run_act_script_generation()
        if res.status is not PartialResultStatus.PASS:
            self.__partial_result = res
            return
        self.write_and_store_script_file_path()
        self.__run_act_script()
        self.__partial_result = self.__execute_assert(phase_env)
        res = self.__run_cleanup(phase_env)
        if res.is_failure:
            self.__partial_result = res

    @property
    def execution_directory_structure(self) -> ExecutionDirectoryStructure:
        if not self.__execution_directory_structure:
            raise ValueError('execution_directory_structure')
        return self.__execution_directory_structure

    @property
    def partial_result(self) -> result.PartialResult:
        return self.__partial_result

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

    @property
    def global_environment(self) -> instructions.GlobalEnvironmentForNamedPhase:
        return self.__global_environment

    def _store_exit_code(self, exitcode: int):
        with open(str(self.execution_directory_structure.result.exitcode_file), 'w') as f:
            f.write(str(exitcode))

    def write_and_store_script_file_path(self):
        script_source = self.__act_env_before_execution.final_script_source
        base_name = self.__file_management.base_name_from_stem(phases.ACT.name)
        file_path = self.__execution_directory_structure.test_case_dir / base_name
        with open(str(file_path), 'w') as f:
            f.write(script_source)
        self.__script_file_path = file_path

    def __run_setup(self, phase_env):
        return self.__run_internal_instructions_phase_step(phases.SETUP,
                                                           None,
                                                           phase_step_executors.SetupPhaseInstructionExecutor(
                                                               self.__global_environment,
                                                               phase_env),
                                                           self.__setup_phase)

    def __execute_assert(self, phase_env):
        return self.__run_internal_instructions_phase_step(phases.ASSERT,
                                                           None,
                                                           phase_step_executors.AssertInstructionExecutor(
                                                               self.__global_environment,
                                                               phase_env),
                                                           self.__assert_phase)

    def __run_cleanup(self, phase_env):
        return self.__run_internal_instructions_phase_step(phases.CLEANUP,
                                                           None,
                                                           phase_step_executors.CleanupPhaseInstructionExecutor(
                                                               self.__global_environment,
                                                               phase_env),
                                                           self.__cleanup_phase)

    def __set_environment_variables(self):
        os.environ[ENV_VAR_HOME] = str(self.configuration.home_dir)
        os.environ[ENV_VAR_TEST] = str(self.execution_directory_structure.test_root_dir)
        os.environ[ENV_VAR_TMP] = str(self.execution_directory_structure.tmp_dir)

    def __run_internal_instructions_phase_step(self,
                                               phase: phases.Phase,
                                               phase_step: str,
                                               instruction_executor: ControlledInstructionExecutor,
                                               phase_contents: PhaseContents) -> PartialResult:
        os.chdir(str(self.execution_directory_structure.test_root_dir))
        return phase_step_executor.execute_phase(phase_contents,
                                                 phase_step_executor.ElementHeaderExecutorThatDoesNothing(),
                                                 phase_step_executor.ElementHeaderExecutorThatDoesNothing(),
                                                 instruction_executor,
                                                 phase,
                                                 phase_step,
                                                 self.execution_directory_structure)

    def __run_act_script_generation(self) -> PartialResult:
        """
        Accumulates the script source by executing all instructions, and adding
        comments from the test case file.

        :param act_environment: Post-condition: Contains the accumulated script source.
        """
        return phase_step_executor.execute_phase(
            self.__act_phase,
            _ActCommentHeaderExecutor(self.__act_env_before_execution),
            _ActInstructionHeaderExecutor(self.__act_env_before_execution),
            phase_step_executors.ActScriptGenerationExecutor(self.__global_environment,
                                                             self.__act_env_before_execution),
            phases.ACT,
            ACT_script_generation,
            self.execution_directory_structure)

    def __run_act_script(self):
        """
        Pre-condition: write has been executed.
        """
        if self.__act_env_before_execution.stdin_file_name:
            try:
                f_stdin = open(self.__act_env_before_execution.stdin_file_name)
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


class _ActCommentHeaderExecutor(ElementHeaderExecutor):
    def __init__(self,
                 phase_environment: instructions.PhaseEnvironmentForScriptGeneration):
        self.__phase_environment = phase_environment

    def apply(self, line: line_source.Line):
        self.__phase_environment.append.comment_line(line)


class _ActInstructionHeaderExecutor(ElementHeaderExecutor):
    def __init__(self,
                 phase_environment: instructions.PhaseEnvironmentForScriptGeneration):
        self.__phase_environment = phase_environment

    def apply(self, line: line_source.Line):
        self.__phase_environment.append.source_line_header(line)


def execute_partial(script_file_manager: script_stmt_gen.ScriptFileManager,
                    script_source_writer: script_stmt_gen.ScriptSourceBuilder,
                    test_case: abs_syn_gen.TestCase,
                    home_dir_path: pathlib.Path,
                    execution_directory_root_name_prefix: str,
                    is_keep_execution_directory_root: bool) -> PartialResult:
    tc_execution = _execute_test_case_in_execution_directory(script_file_manager,
                                                             script_source_writer,
                                                             test_case,
                                                             home_dir_path,
                                                             execution_directory_root_name_prefix,
                                                             is_keep_execution_directory_root)
    return tc_execution.partial_result


def _execute_test_case_in_execution_directory(script_file_manager: script_stmt_gen.ScriptFileManager,
                                              script_source_writer: script_stmt_gen.ScriptSourceBuilder,
                                              test_case: abs_syn_gen.TestCase,
                                              home_dir_path: pathlib.Path,
                                              execution_directory_root_name_prefix: str,
                                              is_keep_execution_directory_root: bool) -> _Executor:
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

    def with_existing_root(exec_dir_structure_root: str) -> _Executor:
        cwd_before = os.getcwd()
        execution_directory_structure = construct_at(exec_dir_structure_root)
        global_environment = instructions.GlobalEnvironmentForNamedPhase(home_dir_path,
                                                                         execution_directory_structure)
        act_environment = instructions.PhaseEnvironmentForScriptGeneration(script_file_manager,
                                                                           script_source_writer)
        configuration = Configuration(home_dir_path,
                                      execution_directory_structure.test_root_dir)

        test_case_execution = _Executor(global_environment,
                                        execution_directory_structure,
                                        configuration,
                                        act_environment,
                                        test_case.setup_phase,
                                        test_case.act_phase,
                                        test_case.assert_phase,
                                        test_case.cleanup_phase)
        try:
            test_case_execution.execute()
        finally:
            os.chdir(cwd_before)
        return test_case_execution

    if is_keep_execution_directory_root:
        tmp_exec_dir_structure_root = tempfile.mkdtemp(prefix=execution_directory_root_name_prefix)
        return with_existing_root(tmp_exec_dir_structure_root)
    else:
        with tempfile.TemporaryDirectory(prefix=execution_directory_root_name_prefix) as tmp_exec_dir_structure_root:
            return with_existing_root(tmp_exec_dir_structure_root)


