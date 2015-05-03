from shelltest.execution import phase_step_executors

__author__ = 'emil'

import tempfile
import os
import subprocess
import pathlib

from shelltest.execution.single_instruction_executor import ControlledInstructionExecutor, execute_element
from shelltest.exec_abs_syn import instructions
from shelltest.phase_instr.model import PhaseContents, PhaseContentElement
from shelltest import phases
from shelltest.exec_abs_syn import script_stmt_gen, abs_syn_gen
from shelltest.exec_abs_syn.config import Configuration
from shelltest import exception
from .execution_directory_structure import construct_at, ExecutionDirectoryStructure
from shelltest.exec_abs_syn.instructions import PhaseEnvironmentForAnonymousPhase, ExecutionMode
from .result import FullResult, PartialResult, PartialResultStatus, FullResultStatus, \
    InstructionFailureInfo, new_partial_result_pass
from . import result


ENV_VAR_HOME = 'SHELLTEST_HOME'
ENV_VAR_TEST = 'SHELLTEST_TESTROOT'
ENV_VAR_TMP = 'SHELLTEST_TMP'

ALL_ENV_VARS = [ENV_VAR_HOME,
                ENV_VAR_TEST,
                ENV_VAR_TMP]


class TestCaseExecution:
    """
    Executes a given Test Case in an existing
    Execution Directory Root.
    """

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

    def write_and_store_script_file_path(self):
        script_source = self.__act_env_before_execution.final_script_source
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
        os.environ[ENV_VAR_TMP] = str(self.execution_directory_structure.tmp_dir)
        phase_env = instructions.PhaseEnvironmentForInternalCommands()
        res = self.__execute_internal_instructions2(phases.SETUP,
                                                    None,
                                                    phase_step_executors.SetupPhaseInstructionExecutor(
                                                        self.__global_environment,
                                                        phase_env),
                                                    self.__setup_phase)
        if res.status is not PartialResultStatus.PASS:
            self.__partial_result = res
            return
        self.__execute_act_phase_to_produce_script_in_act_environment()
        self.write_and_store_script_file_path()
        self.__run_act_script()
        self.__execute_internal_instructions(phases.ASSERT, self.__assert_phase, phase_env)
        self.__execute_internal_instructions(phases.CLEANUP, self.__cleanup_phase, phase_env)

        self.__partial_result = result.new_partial_result_pass(self.execution_directory_structure)

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

    def __execute_internal_instructions(self,
                                        phase: phases.Phase,
                                        phase_contents: PhaseContents,
                                        phase_env: instructions.PhaseEnvironmentForInternalCommands):
        os.chdir(str(self.execution_directory_structure.test_root_dir))
        for element in phase_contents.elements:
            assert isinstance(element, PhaseContentElement)
            if element.is_instruction:
                instruction = element.instruction
                assert isinstance(instruction, instructions.InternalInstruction)
                instruction.execute(phase.name,
                                    self.__global_environment,
                                    phase_env)

    def __execute_internal_instructions2(self,
                                         phase: phases.Phase,
                                         phase_step: str,
                                         instruction_executor: ControlledInstructionExecutor,
                                         phase_contents: PhaseContents) -> PartialResult:
        os.chdir(str(self.execution_directory_structure.test_root_dir))
        return execute_phase(phase_contents,
                             instruction_executor,
                             phase,
                             phase_step,
                             self.execution_directory_structure)

    def __execute_act_phase_to_produce_script_in_act_environment(self):
        """
        Accumulates the script source by executing all instructions, and adding
        comments from the test case file.

        :param act_environment: Post-condition: Contains the accumulated script source.
        """
        for element in self.__act_phase.elements:
            assert isinstance(element, PhaseContentElement)
            if element.is_comment:
                self.__act_env_before_execution.append.comment_line(element.source_line.text)
            else:
                self.__act_env_before_execution.append.source_line_header(element.source_line)
                instruction = element.instruction
                assert isinstance(instruction, instructions.ActPhaseInstruction)
                instruction.update_phase_environment(phases.ACT.name,
                                                     self.__global_environment,
                                                     self.__act_env_before_execution)

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
            instruction = element.instruction
            assert isinstance(instruction, instructions.ActPhaseInstruction)
            instruction.update_phase_environment(phases.ACT.name,
                                                 global_environment,
                                                 act_environment)


def execute_test_case_in_execution_directory(script_file_manager: script_stmt_gen.ScriptFileManager,
                                             script_source_writer: script_stmt_gen.ScriptSourceBuilder,
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
    Please refactor if a more natural responsibility evolves!
    """

    def with_existing_root(exec_dir_structure_root: str) -> TestCaseExecution:
        cwd_before = os.getcwd()
        execution_directory_structure = construct_at(exec_dir_structure_root)
        global_environment = instructions.GlobalEnvironmentForNamedPhase(home_dir_path,
                                                                         execution_directory_structure)
        act_environment = instructions.PhaseEnvironmentForScriptGeneration(script_file_manager,
                                                                           script_source_writer)
        configuration = Configuration(home_dir_path,
                                      execution_directory_structure.test_root_dir)

        test_case_execution = TestCaseExecution(global_environment,
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


def execute_named_phases(script_file_manager: script_stmt_gen.ScriptFileManager,
                         script_source_writer: script_stmt_gen.ScriptSourceBuilder,
                         test_case: abs_syn_gen.TestCase,
                         home_dir_path: pathlib.Path,
                         execution_directory_root_name_prefix: str,
                         is_keep_execution_directory_root: bool) -> PartialResult:
    tc_execution = execute_test_case_in_execution_directory(script_file_manager,
                                                            script_source_writer,
                                                            test_case,
                                                            home_dir_path,
                                                            execution_directory_root_name_prefix,
                                                            is_keep_execution_directory_root)
    return tc_execution.partial_result


def new_anonymous_phase_failure_from(partial_result: PartialResult) -> FullResult:
    full_status = FullResultStatus.HARD_ERROR
    if partial_result.status is PartialResultStatus.IMPLEMENTATION_ERROR:
        full_status = FullResultStatus.IMPLEMENTATION_ERROR
    return FullResult(full_status,
                      None,
                      partial_result.instruction_failure_info)


def new_named_phases_result_from(anonymous_phase_environment: PhaseEnvironmentForAnonymousPhase,
                                 partial_result: PartialResult) -> FullResult:
    def translate_status(ps: PartialResultStatus) -> FullResultStatus:
        if anonymous_phase_environment.execution_mode is ExecutionMode.NORMAL:
            return FullResultStatus(ps.value)
        raise NotImplementedError('not impl statuts translation')

    return FullResult(translate_status(partial_result.status),
                      partial_result.execution_directory_structure,
                      partial_result.instruction_failure_info)


def execute(script_file_manager: script_stmt_gen.ScriptFileManager,
            script_source_writer: script_stmt_gen.ScriptSourceBuilder,
            test_case: abs_syn_gen.TestCase,
            initial_home_dir_path: pathlib.Path,
            execution_directory_root_name_prefix: str,
            is_keep_execution_directory_root: bool) -> FullResult:
    anonymous_phase_environment = PhaseEnvironmentForAnonymousPhase(str(initial_home_dir_path))
    partial_result = execute_anonymous_phase(anonymous_phase_environment,
                                             test_case)
    if partial_result.status is not PartialResultStatus.PASS:
        return new_anonymous_phase_failure_from(partial_result)
    if anonymous_phase_environment.execution_mode is ExecutionMode.SKIPPED:
        return result.new_skipped()
    partial_result = execute_named_phases(script_file_manager,
                                          script_source_writer,
                                          test_case,
                                          anonymous_phase_environment.home_dir_path,
                                          execution_directory_root_name_prefix,
                                          is_keep_execution_directory_root)
    return new_named_phases_result_from(anonymous_phase_environment,
                                        partial_result)


def execute_anonymous_phase(phase_environment: PhaseEnvironmentForAnonymousPhase,
                            test_case: abs_syn_gen.TestCase) -> PartialResult:
    return execute_phase(test_case.anonymous_phase,
                         phase_step_executors.AnonymousPhaseInstructionExecutor(phase_environment),
                         phases.ANONYMOUS,
                         None,
                         None)


def execute_phase(phase_contents: PhaseContents,
                  instruction_executor: ControlledInstructionExecutor,
                  phase: phases.Phase,
                  phase_step: str,
                  eds: ExecutionDirectoryStructure) -> PartialResult:
    for element in phase_contents.elements:
        assert isinstance(element, PhaseContentElement)
        if element.is_instruction:
            failure_info = execute_element(instruction_executor,
                                           element)
            if failure_info is not None:
                return PartialResult(failure_info.status,
                                     eds,
                                     InstructionFailureInfo(phase,
                                                            phase_step,
                                                            failure_info.source_line,
                                                            failure_info.failure_details))
    return new_partial_result_pass(eds)


