import tempfile
import os
import subprocess
import pathlib

from shellcheck_lib.execution import phase_step
from shellcheck_lib.execution import environment_variables
from shellcheck_lib.execution.phase_step import PhaseStep
from shellcheck_lib.execution.phase_step_execution import ElementHeaderExecutor
from shellcheck_lib.general import line_source
from shellcheck_lib.execution import phase_step_executors
from shellcheck_lib.execution.single_instruction_executor import ControlledInstructionExecutor
from shellcheck_lib.general.output import StdOutputFiles
from shellcheck_lib.test_case.sections import common
from shellcheck_lib.document.model import PhaseContents
from shellcheck_lib.execution import phases
from shellcheck_lib.test_case import test_case_doc
from .execution_directory_structure import construct_at, ExecutionDirectoryStructure
from .result import PartialResult, PartialResultStatus, new_partial_result_pass, PhaseFailureInfo
from . import result
from . import phase_step_execution
from shellcheck_lib.test_case.sections.act.phase_setup import PhaseEnvironmentForScriptGeneration, ActProgramExecutor, \
    SourceSetup, ScriptSourceBuilder
from shellcheck_lib.test_case.sections.setup import SetupSettingsBuilder
from shellcheck_lib.test_case.os_services import new_default, OsServices


class Configuration(tuple):
    def __new__(cls,
                home_dir: pathlib.Path,
                act_dir: pathlib.Path):
        return tuple.__new__(cls, (home_dir, act_dir))

    @property
    def home_dir(self) -> pathlib.Path:
        return self[0]

    @property
    def act_dir(self) -> pathlib.Path:
        return self[1]


class _StepExecutionResult:
    def __init__(self):
        self.__script_source = None
        self.__stdin_file_name = None

    @property
    def script_source(self) -> str:
        return self.__script_source

    @script_source.setter
    def script_source(self, x: str):
        self.__script_source = x

    @property
    def stdin_file_name(self) -> str:
        return self.__stdin_file_name

    @stdin_file_name.setter
    def stdin_file_name(self, x: str):
        self.__stdin_file_name = x


class ScriptHandling:
    def __init__(self,
                 builder: ScriptSourceBuilder,
                 executor: ActProgramExecutor):
        self.builder = builder
        self.executor = executor


class PartialExecutor:
    def __init__(self,
                 global_environment: common.GlobalEnvironmentForPostEdsPhase,
                 execution_directory_structure: ExecutionDirectoryStructure,
                 configuration: Configuration,
                 script_handling: ScriptHandling,
                 setup_phase: PhaseContents,
                 act_phase: PhaseContents,
                 assert_phase: PhaseContents,
                 cleanup_phase: PhaseContents):
        self.__global_environment = global_environment
        self.__script_handling = script_handling
        self.__setup_phase = setup_phase
        self.__act_phase = act_phase
        self.__assert_phase = assert_phase
        self.__cleanup_phase = cleanup_phase
        self.__execution_directory_structure = execution_directory_structure
        self.__configuration = configuration
        self.___step_execution_result = _StepExecutionResult()
        self.__source_setup = None
        self.__partial_result = None

    def execute(self):
        """
        Pre-condition: write has been executed.
        """
        # TODO Köra det här i sub-process?
        # Tror det behövs för att undvika att sätta omgivningen mm, o därmed
        # påverka huvudprocessen.
        self.__set_pre_eds_environment_variables()
        res = self.__run_setup_pre_validate()
        if res.status is not PartialResultStatus.PASS:
            self.__partial_result = res
            return
        os_services = new_default()
        self.__set_post_eds_environment_variables()
        res = self.__run_setup_main(os_services)
        if res.status is not PartialResultStatus.PASS:
            self.__partial_result = res
            self.__run_cleanup(os_services)
            return
        res = self.__run_setup_post_validate()
        if res.status is not PartialResultStatus.PASS:
            self.__partial_result = res
            self.__run_cleanup(os_services)
            return
        res = self.__run_act_validate()
        if res.status is not PartialResultStatus.PASS:
            self.__run_cleanup(os_services)
            self.__partial_result = res
            return
        res = self.__run_assert_validate()
        if res.status is not PartialResultStatus.PASS:
            self.__run_cleanup(os_services)
            self.__partial_result = res
            return
        res = self.__run_act_script_generation()
        if res.status is not PartialResultStatus.PASS:
            self.__partial_result = res
            self.__run_cleanup(os_services)
            return
        res = self.__run_act_script_validate()
        if res.status is not PartialResultStatus.PASS:
            self.__partial_result = res
            self.__run_cleanup(os_services)
            return
        res = self.__run_act_script_execute()
        if res.status is not PartialResultStatus.PASS:
            self.__partial_result = res
            self.__run_cleanup(os_services)
            return
        self.__partial_result = self.__run_assert_execute(os_services)
        res = self.__run_cleanup(os_services)
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
    def configuration(self) -> Configuration:
        if not self.__configuration:
            raise ValueError('configuration')
        return self.__configuration

    @property
    def global_environment(self) -> common.GlobalEnvironmentForPostEdsPhase:
        return self.__global_environment

    def _store_exit_code(self, exitcode: int):
        with open(str(self.execution_directory_structure.result.exitcode_file), 'w') as f:
            f.write(str(exitcode))

    def __run_setup_pre_validate(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(phases.SETUP,
                                                           phase_step.SETUP_pre_validate,
                                                           phase_step_executors.SetupPreValidateInstructionExecutor(
                                                               self.__global_environment),
                                                           self.__setup_phase)

    def __run_setup_main(self, os_services: OsServices) -> PartialResult:
        setup_settings_builder = SetupSettingsBuilder()
        ret_val = self.__run_internal_instructions_phase_step(phases.SETUP,
                                                              phase_step.SETUP_execute,
                                                              phase_step_executors.SetupMainInstructionExecutor(
                                                                  os_services,
                                                                  self.__global_environment,
                                                                  setup_settings_builder),
                                                              self.__setup_phase)
        self.___step_execution_result.stdin_file_name = setup_settings_builder.stdin_file_name

        return ret_val

    def __run_setup_post_validate(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(phases.SETUP,
                                                           phase_step.SETUP_post_validate,
                                                           phase_step_executors.SetupPostValidateInstructionExecutor(
                                                               self.__global_environment),
                                                           self.__setup_phase)

    def __run_act_validate(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(phases.ACT,
                                                           phase_step.ACT_validate,
                                                           phase_step_executors.ActValidateInstructionExecutor(
                                                               self.__global_environment),
                                                           self.__act_phase)

    def __run_assert_validate(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(phases.ASSERT,
                                                           phase_step.ASSERT_validate,
                                                           phase_step_executors.AssertValidateInstructionExecutor(
                                                               self.__global_environment),
                                                           self.__assert_phase)

    def __run_assert_execute(self, phase_env) -> PartialResult:
        return self.__run_internal_instructions_phase_step(phases.ASSERT,
                                                           phase_step.ASSERT_execute,
                                                           phase_step_executors.AssertMainInstructionExecutor(
                                                               self.__global_environment,
                                                               phase_env),
                                                           self.__assert_phase)

    def __run_cleanup(self, os_services) -> PartialResult:
        return self.__run_internal_instructions_phase_step(phases.CLEANUP,
                                                           None,
                                                           phase_step_executors.CleanupInstructionExecutor(
                                                               self.__global_environment,
                                                               os_services),
                                                           self.__cleanup_phase)

    def __run_act_script_generation(self) -> PartialResult:
        """
        Accumulates the script source by executing all instructions, and adding
        comments from the test case file.

        :param act_environment: Post-condition: Contains the accumulated script source.
        """
        script_builder = self.__script_handling.builder
        environment = PhaseEnvironmentForScriptGeneration(script_builder)
        os.chdir(str(self.execution_directory_structure.act_dir))
        ret_val = phase_step_execution.execute_phase(
            self.__act_phase,
            _ActCommentHeaderExecutor(environment),
            _ActInstructionHeaderExecutor(environment),
            phase_step_executors.ActScriptGenerationExecutor(self.__global_environment,
                                                             environment),
            phases.ACT,
            phase_step.ACT_script_generate,
            self.execution_directory_structure)
        self.___step_execution_result.script_source = script_builder.build()
        return ret_val

    def __run_act_script_validate(self) -> PartialResult:
        the_phase_step = PhaseStep(phases.ACT, phase_step.ACT_script_validate)
        try:
            res = self.__script_handling.executor.validate(self.__script_handling.builder)
            if res.is_success:
                return new_partial_result_pass(self.__execution_directory_structure)
            else:
                return PartialResult(PartialResultStatus(res.status.value),
                                     self.__execution_directory_structure,
                                     PhaseFailureInfo(the_phase_step,
                                                      result.new_failure_details_from_message(res.failure_message)))
        except Exception as ex:
            return PartialResult(PartialResultStatus.IMPLEMENTATION_ERROR,
                                 self.__execution_directory_structure,
                                 PhaseFailureInfo(the_phase_step,
                                                  result.new_failure_details_from_exception(ex)))

    def __write_and_store_script_file_path(self):
        self.__source_setup = SourceSetup(self.__script_handling.builder,
                                          self.__execution_directory_structure.test_case_dir,
                                          phases.ACT.name)
        self.__script_handling.executor.prepare(self.__source_setup,
                                                self.__execution_directory_structure)

    def __run_act_script_execute(self) -> PartialResult:
        """
        Pre-condition: write has been executed.
        """
        the_phase_step = PhaseStep(phases.ACT, phase_step.ACT_script_execute)
        try:
            self.__write_and_store_script_file_path()
            if self.___step_execution_result.stdin_file_name:
                try:
                    f_stdin = open(self.___step_execution_result.stdin_file_name)
                    self._run_act_script_with_stdin_file(f_stdin)
                finally:
                    f_stdin.close()
            else:
                self._run_act_script_with_stdin_file(subprocess.DEVNULL)
            return new_partial_result_pass(self.__execution_directory_structure)
        except Exception as ex:
            return PartialResult(PartialResultStatus.IMPLEMENTATION_ERROR,
                                 self.__execution_directory_structure,
                                 PhaseFailureInfo(the_phase_step,
                                                  result.new_failure_details_from_exception(ex)))

    def _run_act_script_with_stdin_file(self, f_stdin):
        """
        Pre-condition: write has been executed.
        """
        with open(str(self.execution_directory_structure.result.std.stdout_file), 'w') as f_stdout:
            with open(str(self.execution_directory_structure.result.std.stderr_file), 'w') as f_stderr:
                exitcode = self.__script_handling.executor.execute(
                    self.__source_setup,
                    self.execution_directory_structure.act_dir,
                    self.__execution_directory_structure,
                    f_stdin,
                    StdOutputFiles(f_stdout,
                                   f_stderr))
                self._store_exit_code(exitcode)

    def __set_pre_eds_environment_variables(self):
        os.environ[environment_variables.ENV_VAR_HOME] = str(self.configuration.home_dir)

    def __set_post_eds_environment_variables(self):
        os.environ[environment_variables.ENV_VAR_ACT] = str(self.execution_directory_structure.act_dir)
        os.environ[environment_variables.ENV_VAR_TMP] = str(self.execution_directory_structure.tmp_dir)

    def __run_internal_instructions_phase_step(self,
                                               phase: phases.Phase,
                                               phase_step: str,
                                               instruction_executor: ControlledInstructionExecutor,
                                               phase_contents: PhaseContents) -> PartialResult:
        os.chdir(str(self.execution_directory_structure.act_dir))
        return phase_step_execution.execute_phase(phase_contents,
                                                  phase_step_execution.ElementHeaderExecutorThatDoesNothing(),
                                                  phase_step_execution.ElementHeaderExecutorThatDoesNothing(),
                                                  instruction_executor,
                                                  phase,
                                                  phase_step,
                                                  self.execution_directory_structure)


class _ActCommentHeaderExecutor(ElementHeaderExecutor):
    def __init__(self,
                 phase_environment: PhaseEnvironmentForScriptGeneration):
        self.__phase_environment = phase_environment

    def apply(self, line: line_source.Line):
        self.__phase_environment.append.comment_line(line.text)


class _ActInstructionHeaderExecutor(ElementHeaderExecutor):
    def __init__(self,
                 phase_environment: PhaseEnvironmentForScriptGeneration):
        self.__phase_environment = phase_environment

    def apply(self, line: line_source.Line):
        self.__phase_environment.append.source_line_header(line)


def execute(script_handling: ScriptHandling,
            test_case: test_case_doc.TestCase,
            home_dir_path: pathlib.Path,
            execution_directory_root_name_prefix: str,
            is_keep_execution_directory_root: bool) -> PartialResult:
    tc_execution = execute_test_case_in_execution_directory(script_handling,
                                                            test_case,
                                                            home_dir_path,
                                                            execution_directory_root_name_prefix,
                                                            is_keep_execution_directory_root)
    return tc_execution.partial_result


def execute_test_case_in_execution_directory(script_handling: ScriptHandling,
                                             test_case: test_case_doc.TestCase,
                                             home_dir_path: pathlib.Path,
                                             execution_directory_root_name_prefix: str,
                                             is_keep_execution_directory_root: bool) -> PartialExecutor:
    """
    Takes care of construction of the Execution Directory Structure, including
    the root directory, and executes a given Test Case in this directory.

    Preserves Current Working Directory.

    Perhaps the test case should be executed in a sub process, so that
    Environment Variables and Current Working Directory of the process that executes
    shellcheck is not modified.

    The responsibility of this method is not the most natural!!
    Please refactor if a more natural responsibility evolves!
    """

    def with_existing_root(exec_dir_structure_root: str) -> PartialExecutor:
        cwd_before = os.getcwd()
        execution_directory_structure = construct_at(exec_dir_structure_root)
        global_environment = common.GlobalEnvironmentForPostEdsPhase(home_dir_path,
                                                                     execution_directory_structure)
        configuration = Configuration(home_dir_path,
                                      execution_directory_structure.act_dir)

        test_case_execution = PartialExecutor(global_environment,
                                              execution_directory_structure,
                                              configuration,
                                              script_handling,
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
