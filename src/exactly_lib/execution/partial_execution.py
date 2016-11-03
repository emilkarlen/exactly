import os
import pathlib
import shutil
import subprocess
import tempfile

from exactly_lib.execution import environment_variables
from exactly_lib.execution import phase_step
from exactly_lib.execution import phase_step_executors
from exactly_lib.execution import phases
from exactly_lib.execution.act_phase import ExitCodeOrHardError, ActSourceAndExecutor, \
    ActPhaseHandling, new_eh_hard_error
from exactly_lib.execution.phase_step import PhaseStep
from exactly_lib.execution.single_instruction_executor import ControlledInstructionExecutor
from exactly_lib.section_document.model import SectionContents, ElementType
from exactly_lib.test_case.os_services import new_default
from exactly_lib.test_case.phases import common
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.test_case.phases.cleanup import PreviousPhase
from exactly_lib.test_case.phases.common import GlobalEnvironmentForPreEdsStep, HomeAndEds
from exactly_lib.test_case.phases.setup import SetupSettingsBuilder, StdinSettings
from exactly_lib.util.failure_details import FailureDetails, new_failure_details_from_message, \
    new_failure_details_from_exception
from exactly_lib.util.file_utils import write_new_text_file, resolved_path_name
from exactly_lib.util.std import StdOutputFiles, StdFiles
from . import phase_step_execution
from . import result
from .execution_directory_structure import construct_at, ExecutionDirectoryStructure, stdin_contents_file
from .result import PartialResult, PartialResultStatus, new_partial_result_pass, PhaseFailureInfo


class Configuration(tuple):
    def __new__(cls,
                home_dir_path: pathlib.Path,
                timeout_in_seconds: int = None):
        """
        :param home_dir_path:
        :param timeout_in_seconds: None if no timeout
        """
        return tuple.__new__(cls, (home_dir_path, timeout_in_seconds))

    @property
    def home_dir_path(self) -> pathlib.Path:
        return self[0]

    @property
    def timeout_in_seconds(self) -> int:
        return self[1]


class _ExecutionConfiguration(tuple):
    def __new__(cls,
                configuration: Configuration,
                execution_directory_root_name_prefix: str):
        return tuple.__new__(cls, (configuration, execution_directory_root_name_prefix))

    @property
    def configuration(self) -> Configuration:
        return self[0]

    @property
    def execution_directory_root_name_prefix(self) -> str:
        return self[1]


class TestCase(tuple):
    def __new__(cls,
                setup_phase: SectionContents,
                act_phase: SectionContents,
                before_assert_phase: SectionContents,
                assert_phase: SectionContents,
                cleanup_phase: SectionContents):
        return tuple.__new__(cls, (setup_phase,
                                   act_phase,
                                   before_assert_phase,
                                   assert_phase,
                                   cleanup_phase))

    @property
    def setup_phase(self) -> SectionContents:
        return self[0]

    @property
    def act_phase(self) -> SectionContents:
        return self[1]

    @property
    def before_assert_phase(self) -> SectionContents:
        return self[2]

    @property
    def assert_phase(self) -> SectionContents:
        return self[3]

    @property
    def cleanup_phase(self) -> SectionContents:
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


def execute(act_phase_handling: ActPhaseHandling,
            test_case: TestCase,
            configuration: Configuration,
            initial_setup_settings: SetupSettingsBuilder,
            execution_directory_root_name_prefix: str,
            is_keep_execution_directory_root: bool) -> PartialResult:
    """
    Takes care of construction of the Execution Directory Structure, including
    the root directory, and executes a given Test Case in this directory.

    Preserves Current Working Directory.

    Perhaps the test case should be executed in a sub process, so that
    Environment Variables and Current Working Directory of the process that executes
    the main program is not modified.

    The responsibility of this method is not the most natural!!
    Please refactor if a more natural responsibility evolves!
    """
    cwd_before = None
    ret_val = None
    try:
        cwd_before = os.getcwd()
        exe_configuration = _ExecutionConfiguration(configuration,
                                                    execution_directory_root_name_prefix)

        test_case_execution = _PartialExecutor(exe_configuration,
                                               act_phase_handling,
                                               test_case,
                                               initial_setup_settings)
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
    return construct_at(resolved_path_name(eds_structure_root))


class _PartialExecutor:
    def __init__(self,
                 exe_configuration: _ExecutionConfiguration,
                 act_phase_handling: ActPhaseHandling,
                 test_case: TestCase,
                 setup_settings_builder: SetupSettingsBuilder):
        self.__execution_directory_structure = None
        self.__global_environment_pre_eds = GlobalEnvironmentForPreEdsStep(
            exe_configuration.configuration.home_dir_path)
        self.__act_phase_handling = act_phase_handling
        self.__test_case = test_case
        self.__exe_configuration = exe_configuration
        self.__configuration = exe_configuration.configuration
        self.__setup_settings_builder = setup_settings_builder
        self.___step_execution_result = _StepExecutionResult()
        self.__source_setup = None
        self.os_services = None
        self.__act_source_and_executor = None
        self.__act_source_and_executor_constructor = act_phase_handling.source_and_executor_constructor

    def execute(self) -> PartialResult:
        # TODO Köra det här i sub-process?
        # Tror det behövs för att undvika att sätta omgivningen mm, o därmed
        # påverka huvudprocessen.
        self.__set_pre_eds_environment_variables()
        res = self._sequence([
            self.__setup__validate_pre_eds,
            self.__act__create_executor_and_validate_pre_eds,
            self.__before_assert__validate_pre_eds,
            self.__assert__validate_pre_eds,
            self.__cleanup__validate_pre_eds,
        ])
        if res.is_failure:
            return res
        self._setup_post_eds_environment()
        act_program_executor = self.__act_program_executor()
        res = self._sequence_with_cleanup(
            PreviousPhase.SETUP,
            [
                self.__setup__main,
                self.__setup__validate_post_setup,
                act_program_executor.validate_post_setup,
                self.__before_assert__validate_post_setup,
                self.__assert__validate_post_setup,
                act_program_executor.prepare,
                act_program_executor.execute,
            ])
        if res.is_failure:
            return res
        self.__set_assert_environment_variables()
        res = self.__before_assert__main()
        if res.is_failure:
            self.__cleanup_main(PreviousPhase.BEFORE_ASSERT)
            return res
        ret_val = self.__assert__main()
        res = self.__cleanup_main(PreviousPhase.ASSERT)
        if res.is_failure:
            ret_val = res
        return ret_val

    def _sequence(self, actions: list) -> PartialResult:
        for action in actions:
            res = action()
            if res.is_failure:
                return res
        return new_partial_result_pass(self._eds)

    def _sequence_with_cleanup(self, previous_phase: PreviousPhase, actions: list) -> PartialResult:
        for action in actions:
            res = action()
            if res.is_failure:
                self.__cleanup_main(previous_phase)
                return res
        return new_partial_result_pass(self._eds)

    @property
    def _eds(self) -> ExecutionDirectoryStructure:
        return self.__execution_directory_structure

    @property
    def exe_configuration(self) -> _ExecutionConfiguration:
        return self.__exe_configuration

    @property
    def configuration(self) -> Configuration:
        return self.__configuration

    def _setup_post_eds_environment(self):
        self.__construct_and_set_eds()
        self.os_services = new_default()
        self.__set_cwd_to_act_dir()
        self.__set_post_eds_environment_variables()

    def __setup__validate_pre_eds(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(phase_step.SETUP__VALIDATE_PRE_EDS,
                                                           phase_step_executors.SetupValidatePreEdsExecutor(
                                                               self.__global_environment_pre_eds),
                                                           self.__test_case.setup_phase)

    def __act__create_executor_and_validate_pre_eds(self) -> PartialResult:
        failure_con = _PhaseFailureResultConstructor(phase_step.ACT__VALIDATE_PRE_EDS, None)

        def action():
            section_contents = self.__test_case.act_phase
            instructions = []
            for element in section_contents.elements:
                if element.element_type is ElementType.INSTRUCTION:
                    instruction = element.instruction
                    if not isinstance(instruction, ActPhaseInstruction):
                        msg = 'Instruction is not an instance of ' + str(ActPhaseInstruction)
                        return failure_con.implementation_error_msg(msg)
                    instructions.append(instruction)
                else:
                    msg = 'Act phase contains an element that is not an instruction: ' + str(element.element_type)
                    return failure_con.implementation_error_msg(msg)

            self.__act_source_and_executor = self.__act_phase_handling.source_and_executor_constructor.apply(
                self.__global_environment_pre_eds,
                instructions)
            res = self.__act_source_and_executor.validate_pre_eds(self.__global_environment_pre_eds.home_directory)
            if res.is_success:
                return new_partial_result_pass(None)
            else:
                return failure_con.apply(PartialResultStatus(res.status.value),
                                         new_failure_details_from_message(res.failure_message))

        try:
            return action()
        except Exception as ex:
            return PartialResult(PartialResultStatus.IMPLEMENTATION_ERROR,
                                 None,
                                 PhaseFailureInfo(phase_step.ACT__VALIDATE_PRE_EDS,
                                                  new_failure_details_from_exception(ex)))

    def __before_assert__validate_pre_eds(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(
            phase_step.BEFORE_ASSERT__VALIDATE_PRE_EDS,
            phase_step_executors.BeforeAssertValidatePreEdsExecutor(self.__global_environment_pre_eds),
            self.__test_case.before_assert_phase)

    def __assert__validate_pre_eds(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(phase_step.ASSERT__VALIDATE_PRE_EDS,
                                                           phase_step_executors.AssertValidatePreEdsExecutor(
                                                               self.__global_environment_pre_eds),
                                                           self.__test_case.assert_phase)

    def __cleanup__validate_pre_eds(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(phase_step.CLEANUP__VALIDATE_PRE_EDS,
                                                           phase_step_executors.CleanupValidatePreEdsExecutor(
                                                               self.__global_environment_pre_eds),
                                                           self.__test_case.cleanup_phase)

    def __setup__main(self) -> PartialResult:
        ret_val = self.__run_internal_instructions_phase_step(phase_step.SETUP__MAIN,
                                                              phase_step_executors.SetupMainExecutor(
                                                                  self.os_services,
                                                                  self.__post_eds_environment(phases.SETUP),
                                                                  self.__setup_settings_builder),
                                                              self.__test_case.setup_phase)
        self.___step_execution_result.stdin_settings = self.__setup_settings_builder.stdin

        return ret_val

    def __setup__validate_post_setup(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(
            phase_step.SETUP__VALIDATE_POST_SETUP,
            phase_step_executors.SetupValidatePostSetupExecutor(
                self.__post_eds_environment(phases.SETUP)),
            self.__test_case.setup_phase)

    def __act_program_executor(self):
        return _ActProgramExecution(self.__act_source_and_executor,
                                    HomeAndEds(self.__configuration.home_dir_path, self._eds),
                                    self.___step_execution_result)

    def __before_assert__validate_post_setup(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(
            phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
            phase_step_executors.BeforeAssertValidatePostSetupExecutor(
                self.__post_eds_environment(phases.BEFORE_ASSERT)),
            self.__test_case.before_assert_phase)

    def __assert__validate_post_setup(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(
            phase_step.ASSERT__VALIDATE_POST_SETUP,
            phase_step_executors.AssertValidatePostSetupExecutor(
                self.__post_eds_environment(phases.ASSERT)),
            self.__test_case.assert_phase)

    def __assert__main(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(
            phase_step.ASSERT__MAIN,
            phase_step_executors.AssertMainExecutor(
                self.__post_eds_environment(phases.ASSERT),
                self.os_services),
            self.__test_case.assert_phase)

    def __cleanup_main(self, previous_phase: PreviousPhase) -> PartialResult:
        return self.__run_internal_instructions_phase_step(
            phase_step.CLEANUP__MAIN,
            phase_step_executors.CleanupMainExecutor(
                self.__post_eds_environment(phases.CLEANUP),
                previous_phase,
                self.os_services),
            self.__test_case.cleanup_phase)

    def __before_assert__main(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(
            phase_step.BEFORE_ASSERT__MAIN,
            phase_step_executors.BeforeAssertMainExecutor(
                self.__post_eds_environment(phases.BEFORE_ASSERT),
                self.os_services),
            self.__test_case.before_assert_phase)

    def __set_pre_eds_environment_variables(self):
        os.environ.update(environment_variables.set_at_setup_pre_validate(self.__configuration.home_dir_path))

    def __set_cwd_to_act_dir(self):
        os.chdir(str(self._eds.act_dir))

    def __construct_and_set_eds(self) -> ExecutionDirectoryStructure:
        eds_structure_root = tempfile.mkdtemp(prefix=self.__exe_configuration.execution_directory_root_name_prefix)
        self.__execution_directory_structure = construct_eds(eds_structure_root)

    def __post_eds_environment(self,
                               phase: phases.Phase) -> common.GlobalEnvironmentForPostEdsPhase:
        return common.GlobalEnvironmentForPostEdsPhase(self.__configuration.home_dir_path,
                                                       self.__execution_directory_structure,
                                                       phase.identifier)

    def __set_post_eds_environment_variables(self):
        os.environ.update(environment_variables.set_at_setup_main(self._eds))

    def __set_assert_environment_variables(self):
        os.environ.update(environment_variables.set_at_assert(self._eds))

    def __run_internal_instructions_phase_step(self,
                                               step: PhaseStep,
                                               instruction_executor: ControlledInstructionExecutor,
                                               phase_contents: SectionContents) -> PartialResult:
        return phase_step_execution.execute_phase(phase_contents,
                                                  phase_step_execution.ElementHeaderExecutorThatDoesNothing(),
                                                  phase_step_execution.ElementHeaderExecutorThatDoesNothing(),
                                                  instruction_executor,
                                                  step,
                                                  self._eds)


class _PhaseFailureResultConstructor:
    def __init__(self,
                 step: PhaseStep,
                 eds: ExecutionDirectoryStructure):
        self.step = step
        self.eds = eds

    def apply(self,
              status: PartialResultStatus,
              failure_details: FailureDetails) -> PartialResult:
        return PartialResult(status,
                             self.eds,
                             result.PhaseFailureInfo(self.step,
                                                     failure_details))

    def implementation_error(self, ex: Exception) -> PartialResult:
        return self.apply(PartialResultStatus.IMPLEMENTATION_ERROR,
                          new_failure_details_from_exception(ex))

    def implementation_error_msg(self, msg: str) -> PartialResult:
        return self.apply(PartialResultStatus.IMPLEMENTATION_ERROR,
                          new_failure_details_from_message(msg))


class _ActProgramExecution:
    def __init__(self,
                 act_source_and_executor: ActSourceAndExecutor,
                 home_and_eds: HomeAndEds,
                 step_execution_result: _StepExecutionResult()):
        self.act_source_and_executor = act_source_and_executor
        self.home_and_eds = home_and_eds
        self.step_execution_result = step_execution_result
        self.script_output_dir_path = self.home_and_eds.eds.test_case_dir

    def validate_post_setup(self) -> PartialResult:
        step = phase_step.ACT__VALIDATE_POST_SETUP

        def action():
            res = self.act_source_and_executor.validate_post_setup(self.home_and_eds)
            if res.is_success:
                return self._pass()
            else:
                return self._failure_from(step,
                                          PartialResultStatus(res.status.value),
                                          new_failure_details_from_message(res.failure_message))

        return self._with_implementation_exception_handling(step, action)

    def prepare(self) -> PartialResult:
        step = phase_step.ACT__PREPARE

        def action():
            res = self.act_source_and_executor.prepare(self.home_and_eds,
                                                       self.script_output_dir_path)
            if res.is_success:
                return self._pass()
            else:
                return self._failure_from(step,
                                          PartialResultStatus.HARD_ERROR,
                                          new_failure_details_from_message(res.failure_message))

        return self._with_implementation_exception_handling(step, action)

    def execute(self) -> PartialResult:
        step = phase_step.ACT__EXECUTE

        def action():
            exit_code_or_hard_error = self._execute_with_stdin_handling()
            if exit_code_or_hard_error.is_exit_code:
                return self._pass()
            else:
                return self._failure_from(step,
                                          PartialResultStatus.HARD_ERROR,
                                          exit_code_or_hard_error.failure_details)

        return self._with_implementation_exception_handling(step, action)

    def _execute_with_stdin_handling(self) -> ExitCodeOrHardError:
        if self.step_execution_result.has_custom_stdin:
            file_name = self._custom_stdin_file_name()
            return self._run_act_program_with_opened_stdin_file(file_name)
        else:
            return self._run_act_program_with_stdin_file(subprocess.DEVNULL)

    def _run_act_program_with_opened_stdin_file(self, file_name: str) -> ExitCodeOrHardError:
        try:
            with open(file_name) as f_stdin:
                return self._run_act_program_with_stdin_file(f_stdin)
        except IOError as ex:
            return new_eh_hard_error(new_failure_details_from_exception(ex,
                                                                        'Failure to open stdin file: ' + file_name))

    def _run_act_program_with_stdin_file(self, f_stdin) -> ExitCodeOrHardError:
        """
        Pre-condition: write has been executed.
        """
        eds = self.home_and_eds.eds
        with open(str(eds.result.stdout_file), 'w') as f_stdout:
            with open(str(eds.result.stderr_file), 'w') as f_stderr:
                exit_code_or_hard_error = self.act_source_and_executor.execute(
                    self.home_and_eds,
                    self.script_output_dir_path,
                    StdFiles(f_stdin,
                             StdOutputFiles(f_stdout,
                                            f_stderr)))
                if exit_code_or_hard_error.is_exit_code:
                    self._store_exit_code(exit_code_or_hard_error.exit_code)
                return exit_code_or_hard_error

    def _store_exit_code(self, exitcode: int):
        with open(str(self.home_and_eds.eds.result.exitcode_file), 'w') as f:
            f.write(str(exitcode))

    def _custom_stdin_file_name(self) -> str:
        settings = self.step_execution_result.stdin_settings
        if settings.file_name is not None:
            return settings.file_name
        else:
            file_path = stdin_contents_file(self.home_and_eds.eds)
            write_new_text_file(file_path, settings.contents)
            return str(file_path)

    def _with_implementation_exception_handling(self, step: phase_step.PhaseStep, action) -> PartialResult:
        try:
            return action()
        except Exception as ex:
            return self._failure_con_for(step).implementation_error(ex)

    def _pass(self) -> PartialResult:
        return new_partial_result_pass(self.home_and_eds.eds)

    def _failure_from(self,
                      step: PhaseStep,
                      status: PartialResultStatus,
                      failure_details: FailureDetails) -> PartialResult:
        return self._failure_con_for(step).apply(status, failure_details)

    def _failure_con_for(self, step: PhaseStep) -> _PhaseFailureResultConstructor:
        return _PhaseFailureResultConstructor(step, self.home_and_eds.eds)
