import os
import pathlib
import shutil
import subprocess
import tempfile

from shellcheck_lib.document.model import PhaseContents
from shellcheck_lib.execution import environment_variables
from shellcheck_lib.execution import phase_step
from shellcheck_lib.execution import phase_step_executors
from shellcheck_lib.execution import phases
from shellcheck_lib.execution.phase_step import PhaseStep
from shellcheck_lib.execution.phase_step_execution import ElementHeaderExecutor
from shellcheck_lib.execution.single_instruction_executor import ControlledInstructionExecutor
from shellcheck_lib.general import line_source
from shellcheck_lib.general.file_utils import write_new_text_file
from shellcheck_lib.general.std import StdOutputFiles, StdFiles
from shellcheck_lib.test_case.os_services import new_default, OsServices
from shellcheck_lib.test_case.sections import common
from shellcheck_lib.test_case.sections.act.phase_setup import PhaseEnvironmentForScriptGeneration, ActProgramExecutor, \
    SourceSetup, ScriptSourceBuilder
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.sections.setup import SetupSettingsBuilder, StdinSettings
from . import phase_step_execution
from . import result
from .execution_directory_structure import construct_at, ExecutionDirectoryStructure, stdin_contents_file
from .result import PartialResult, PartialResultStatus, new_partial_result_pass, PhaseFailureInfo


class Configuration(tuple):
    def __new__(cls,
                home_dir: pathlib.Path,
                execution_directory_root_name_prefix: str):
        return tuple.__new__(cls, (home_dir, execution_directory_root_name_prefix))

    @property
    def home_dir(self) -> pathlib.Path:
        return self[0]

    @property
    def execution_directory_root_name_prefix(self) -> str:
        return self[1]


class TestCase(tuple):
    def __new__(cls,
                setup_phase: PhaseContents,
                act_phase: PhaseContents,
                before_assert_phase: PhaseContents,
                assert_phase: PhaseContents,
                cleanup_phase: PhaseContents):
        return tuple.__new__(cls, (setup_phase,
                                   act_phase,
                                   before_assert_phase,
                                   assert_phase,
                                   cleanup_phase))

    @property
    def setup_phase(self) -> PhaseContents:
        return self[0]

    @property
    def act_phase(self) -> PhaseContents:
        return self[1]

    @property
    def before_assert_phase(self) -> PhaseContents:
        return self[2]

    @property
    def assert_phase(self) -> PhaseContents:
        return self[3]

    @property
    def cleanup_phase(self) -> PhaseContents:
        return self[4]


class _StepExecutionResult:
    def __init__(self):
        self.__script_source = None
        self.__stdin_settings = None

    @property
    def script_source(self) -> str:
        return self.__script_source

    @script_source.setter
    def script_source(self, x: str):
        self.__script_source = x

    @property
    def has_custom_stdin(self) -> bool:
        return self.__stdin_settings.file_name is not None or \
               self.__stdin_settings.contents is not None

    @property
    def stdin_settings(self) -> StdinSettings:
        return self.__stdin_settings

    @stdin_settings.setter
    def stdin_settings(self, x: StdinSettings):
        self.__stdin_settings = x


class ScriptHandling:
    def __init__(self,
                 builder: ScriptSourceBuilder,
                 executor: ActProgramExecutor):
        self.builder = builder
        self.executor = executor


def execute(script_handling: ScriptHandling,
            test_case: TestCase,
            home_dir_path: pathlib.Path,
            execution_directory_root_name_prefix: str,
            is_keep_execution_directory_root: bool) -> PartialResult:
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
    cwd_before = None
    ret_val = None
    try:
        cwd_before = os.getcwd()
        configuration = Configuration(home_dir_path,
                                      execution_directory_root_name_prefix)

        test_case_execution = PartialExecutor(configuration,
                                              script_handling,
                                              test_case)
        ret_val = test_case_execution.execute()
        return ret_val
    finally:
        if cwd_before is not None:
            os.chdir(cwd_before)
        if not is_keep_execution_directory_root:
            if ret_val is not None and ret_val.has_execution_directory_structure:
                shutil.rmtree(str(ret_val.execution_directory_structure.root_dir))


def construct_eds(execution_directory_root_name_prefix: str) -> ExecutionDirectoryStructure:
    eds_structure_root = tempfile.mkdtemp(prefix=execution_directory_root_name_prefix)
    return construct_at(eds_structure_root)


class PartialExecutor:
    def __init__(self,
                 configuration: Configuration,
                 script_handling: ScriptHandling,
                 test_case: TestCase):
        self.__execution_directory_structure = None
        self.__global_environment = GlobalEnvironmentForPreEdsStep(configuration.home_dir)
        self.__script_handling = script_handling
        self.__test_case = test_case
        self.__configuration = configuration
        self.___step_execution_result = _StepExecutionResult()
        self.__source_setup = None

    def execute(self) -> PartialResult:
        # TODO Köra det här i sub-process?
        # Tror det behövs för att undvika att sätta omgivningen mm, o därmed
        # påverka huvudprocessen.
        self.__set_pre_eds_environment_variables()
        res = self.__run_setup_pre_validate()
        if res.status is not PartialResultStatus.PASS:
            return res
        res = self.__run_act__validate_pre_eds()
        if res.status is not PartialResultStatus.PASS:
            return res
        res = self.__run_before_assert__validate_pre_eds()
        if res.status is not PartialResultStatus.PASS:
            return res
        res = self.__run_assert__validate_pre_eds()
        if res.status is not PartialResultStatus.PASS:
            return res
        res = self.__run_cleanup__validate_pre_eds()
        if res.status is not PartialResultStatus.PASS:
            return res
        self.__construct_and_set_eds()
        self.__set_post_eds_environment()
        os_services = new_default()
        self.__set_cwd_to_act_dir()
        self.__set_post_eds_environment_variables()
        res = self.__run_setup_main(os_services)
        if res.status is not PartialResultStatus.PASS:
            self.__run_cleanup(os_services)
            return res
        res = self.__run_setup_post_validate()
        if res.status is not PartialResultStatus.PASS:
            self.__run_cleanup(os_services)
            return res
        res = self.__run_act_validate()
        if res.status is not PartialResultStatus.PASS:
            self.__run_cleanup(os_services)
            return res
        res = self.__run_before_assert__validate_post_setup()
        if res.status is not PartialResultStatus.PASS:
            self.__run_cleanup(os_services)
            return res
        res = self.__run_assert_validate()
        if res.status is not PartialResultStatus.PASS:
            self.__run_cleanup(os_services)
            return res
        res = self.__run_act_script_generation()
        if res.status is not PartialResultStatus.PASS:
            self.__run_cleanup(os_services)
            return res
        res = self.__run_act_script_validate()
        if res.status is not PartialResultStatus.PASS:
            self.__run_cleanup(os_services)
            return res
        res = self.__run_act_script_execute()
        if res.status is not PartialResultStatus.PASS:
            self.__run_cleanup(os_services)
            return res
        self.__set_assert_environment_variables()
        res = self.__run_before_assert_main(os_services)
        if res.status is not PartialResultStatus.PASS:
            self.__run_cleanup(os_services)
            return res
        ret_val = self.__run_assert_execute(os_services)
        res = self.__run_cleanup(os_services)
        if res.is_failure:
            ret_val = res
        return ret_val

    @property
    def _eds(self) -> ExecutionDirectoryStructure:
        return self.__execution_directory_structure

    @property
    def configuration(self) -> Configuration:
        return self.__configuration

    @property
    def global_environment(self) -> common.GlobalEnvironmentForPostEdsPhase:
        return self.__global_environment

    def _store_exit_code(self, exitcode: int):
        with open(str(self._eds.result.exitcode_file), 'w') as f:
            f.write(str(exitcode))

    def __run_setup_pre_validate(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(phase_step.SETUP_VALIDATE_PRE_EDS,
                                                           phase_step_executors.SetupPreValidateInstructionExecutor(
                                                                   self.__global_environment),
                                                           self.__test_case.setup_phase)

    def __run_act__validate_pre_eds(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(phase_step.ACT_VALIDATE_PRE_EDS,
                                                           phase_step_executors.ActPreValidateInstructionExecutor(
                                                                   self.__global_environment),
                                                           self.__test_case.act_phase)

    def __run_before_assert__validate_pre_eds(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(
                phase_step.BEFORE_ASSERT_VALIDATE_PRE_EDS,
                phase_step_executors.BeforeAssertPreValidateInstructionExecutor(self.__global_environment),
                self.__test_case.before_assert_phase)

    def __run_assert__validate_pre_eds(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(phase_step.ASSERT_VALIDATE_PRE_EDS,
                                                           phase_step_executors.AssertPreValidateInstructionExecutor(
                                                                   self.__global_environment),
                                                           self.__test_case.assert_phase)

    def __run_cleanup__validate_pre_eds(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(phase_step.CLEANUP_VALIDATE_PRE_EDS,
                                                           phase_step_executors.CleanupPreValidateInstructionExecutor(
                                                                   self.__global_environment),
                                                           self.__test_case.cleanup_phase)

    def __run_setup_main(self, os_services: OsServices) -> PartialResult:
        setup_settings_builder = SetupSettingsBuilder()
        ret_val = self.__run_internal_instructions_phase_step(phase_step.SETUP_MAIN,
                                                              phase_step_executors.SetupMainInstructionExecutor(
                                                                      os_services,
                                                                      self.__global_environment,
                                                                      setup_settings_builder),
                                                              self.__test_case.setup_phase)
        self.___step_execution_result.stdin_settings = setup_settings_builder.stdin

        return ret_val

    def __run_setup_post_validate(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(phase_step.SETUP_VALIDATE_POST_EDS,
                                                           phase_step_executors.SetupPostValidateInstructionExecutor(
                                                                   self.__global_environment),
                                                           self.__test_case.setup_phase)

    def __run_act_validate(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(phase_step.ACT_VALIDATE_POST_SETUP,
                                                           phase_step_executors.ActValidateInstructionExecutor(
                                                                   self.__global_environment),
                                                           self.__test_case.act_phase)

    def __run_act_script_generation(self) -> PartialResult:
        """
        Accumulates the script source by executing all instructions, and adding
        comments from the test case file.

        :param act_environment: Post-condition: Contains the accumulated script source.
        """
        script_builder = self.__script_handling.builder
        environment = PhaseEnvironmentForScriptGeneration(script_builder)
        ret_val = phase_step_execution.execute_phase(
                self.__test_case.act_phase,
                _ActCommentHeaderExecutor(environment),
                _ActInstructionHeaderExecutor(environment),
                phase_step_executors.ActMainInstructionExecutor(self.__global_environment,
                                                                environment),
                phase_step.ACT_MAIN,
                self._eds)
        self.___step_execution_result.script_source = script_builder.build()
        return ret_val

    def __run_act_script_validate(self) -> PartialResult:
        the_phase_step = phase_step.ACT_SCRIPT_VALIDATE
        try:
            res = self.__script_handling.executor.validate(self.configuration.home_dir,
                                                           self.__script_handling.builder)
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

    def __run_before_assert__validate_post_setup(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(
                phase_step.BEFORE_ASSERT_VALIDATE_POST_EDS,
                phase_step_executors.BeforeAssertValidatePostSetupInstructionExecutor(
                        self.__global_environment),
                self.__test_case.before_assert_phase)

    def __run_assert_validate(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(phase_step.ASSERT_VALIDATE_POST_EDS,
                                                           phase_step_executors.AssertValidateInstructionExecutor(
                                                                   self.__global_environment),
                                                           self.__test_case.assert_phase)

    def __run_assert_execute(self, phase_env) -> PartialResult:
        return self.__run_internal_instructions_phase_step(phase_step.ASSERT_MAIN,
                                                           phase_step_executors.AssertMainInstructionExecutor(
                                                                   self.__global_environment,
                                                                   phase_env),
                                                           self.__test_case.assert_phase)

    def __run_cleanup(self, os_services) -> PartialResult:
        return self.__run_internal_instructions_phase_step(phase_step.CLEANUP_MAIN,
                                                           phase_step_executors.CleanupInstructionExecutor(
                                                                   self.__global_environment,
                                                                   os_services),
                                                           self.__test_case.cleanup_phase)

    def __run_before_assert_main(self, os_services) -> PartialResult:
        return self.__run_internal_instructions_phase_step(phase_step.BEFORE_ASSERT_MAIN,
                                                           phase_step_executors.BeforeAssertInstructionExecutor(
                                                                   self.__global_environment,
                                                                   os_services),
                                                           self.__test_case.before_assert_phase)

    def __write_and_store_script_file_path(self):
        self.__source_setup = SourceSetup(self.__script_handling.builder,
                                          self.__execution_directory_structure.test_case_dir,
                                          phases.ACT.section_name)
        self.__script_handling.executor.prepare(self.__source_setup,
                                                self.configuration.home_dir,
                                                self.__execution_directory_structure)

    def __run_act_script_execute(self) -> PartialResult:
        """
        Pre-condition: write has been executed.
        """
        the_phase_step = phase_step.ACT_SCRIPT_EXECUTE
        try:
            self.__write_and_store_script_file_path()
            if self.___step_execution_result.has_custom_stdin:
                file_name = self._custom_stdin_file_name()
                self._run_act_script_with_opened_stdin_file(file_name)
            else:
                self._run_act_script_with_stdin_file(subprocess.DEVNULL)
            return new_partial_result_pass(self.__execution_directory_structure)
        except Exception as ex:
            return PartialResult(PartialResultStatus.IMPLEMENTATION_ERROR,
                                 self.__execution_directory_structure,
                                 PhaseFailureInfo(the_phase_step,
                                                  result.new_failure_details_from_exception(ex)))

    def _run_act_script_with_opened_stdin_file(self, file_name: str):
        try:
            f_stdin = open(file_name)
            self._run_act_script_with_stdin_file(f_stdin)
        finally:
            f_stdin.close()

    def _run_act_script_with_stdin_file(self, f_stdin):
        """
        Pre-condition: write has been executed.
        """
        with open(str(self._eds.result.stdout_file), 'w') as f_stdout:
            with open(str(self._eds.result.stderr_file), 'w') as f_stderr:
                exitcode = self.__script_handling.executor.execute(
                        self.__source_setup,
                        self.configuration.home_dir,
                        self.__execution_directory_structure,
                        StdFiles(f_stdin,
                                 StdOutputFiles(f_stdout,
                                                f_stderr)))
                self._store_exit_code(exitcode)

    def __set_pre_eds_environment_variables(self):
        os.environ.update(environment_variables.set_at_setup_pre_validate(self.configuration.home_dir))

    def __set_cwd_to_act_dir(self):
        os.chdir(str(self._eds.act_dir))

    def __construct_and_set_eds(self) -> ExecutionDirectoryStructure:
        eds_structure_root = tempfile.mkdtemp(prefix=self.__configuration.execution_directory_root_name_prefix)
        self.__execution_directory_structure = construct_eds(eds_structure_root)

    def __set_post_eds_environment(self):
        self.__global_environment = common.GlobalEnvironmentForPostEdsPhase(self.__configuration.home_dir,
                                                                            self.__execution_directory_structure)

    def __set_post_eds_environment_variables(self):
        os.environ.update(environment_variables.set_at_setup_main(self._eds))

    def __set_assert_environment_variables(self):
        os.environ.update(environment_variables.set_at_assert(self._eds))

    def __run_internal_instructions_phase_step(self,
                                               step: PhaseStep,
                                               instruction_executor: ControlledInstructionExecutor,
                                               phase_contents: PhaseContents) -> PartialResult:
        return phase_step_execution.execute_phase(phase_contents,
                                                  phase_step_execution.ElementHeaderExecutorThatDoesNothing(),
                                                  phase_step_execution.ElementHeaderExecutorThatDoesNothing(),
                                                  instruction_executor,
                                                  step,
                                                  self._eds)

    def _custom_stdin_file_name(self) -> str:
        settings = self.___step_execution_result.stdin_settings
        if settings.file_name is not None:
            return settings.file_name
        else:
            file_path = stdin_contents_file(self.__execution_directory_structure)
            write_new_text_file(file_path, settings.contents)
            return str(file_path)


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
