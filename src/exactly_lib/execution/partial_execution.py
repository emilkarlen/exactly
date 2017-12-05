import os
import pathlib
import shutil
import subprocess
import tempfile

from exactly_lib.execution.instruction_execution import phase_step_executors, phase_step_execution
from exactly_lib.execution.instruction_execution.single_instruction_executor import ControlledInstructionExecutor
from exactly_lib.execution.phase_step_identifiers import phase_step
from exactly_lib.execution.phase_step_identifiers.phase_step import PhaseStep
from exactly_lib.section_document.model import SectionContents, ElementType
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.act_phase_handling import ActSourceAndExecutor, \
    ActPhaseHandling, ActPhaseOsProcessExecutor, ParseException
from exactly_lib.test_case.eh import ExitCodeOrHardError, new_eh_hard_error
from exactly_lib.test_case.os_services import new_default
from exactly_lib.test_case.phases import common
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.cleanup import PreviousPhase
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.setup import SetupSettingsBuilder, StdinSettings
from exactly_lib.test_case_file_structure import environment_variables
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.sandbox_directory_structure import construct_at, SandboxDirectoryStructure, \
    stdin_contents_file
from exactly_lib.util.failure_details import FailureDetails, new_failure_details_from_message, \
    new_failure_details_from_exception
from exactly_lib.util.file_utils import write_new_text_file, resolved_path_name, preserved_cwd, \
    open_and_make_read_only_on_close
from exactly_lib.util.std import StdOutputFiles, StdFiles
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from . import result
from .result import PartialResult, PartialResultStatus, new_partial_result_pass, PhaseFailureInfo


class Configuration(tuple):
    def __new__(cls,
                act_phase_os_process_executor: ActPhaseOsProcessExecutor,
                hds: HomeDirectoryStructure,
                environ: dict,
                timeout_in_seconds: int = None,
                predefined_symbols: SymbolTable = None):
        """
        :param timeout_in_seconds: None if no timeout
        """
        return tuple.__new__(cls, (hds,
                                   timeout_in_seconds,
                                   environ,
                                   act_phase_os_process_executor,
                                   symbol_table_from_none_or_value(predefined_symbols)))

    @property
    def act_phase_os_process_executor(self) -> ActPhaseOsProcessExecutor:
        return self[3]

    @property
    def hds(self) -> HomeDirectoryStructure:
        return self[0]

    @property
    def timeout_in_seconds(self) -> int:
        return self[1]

    @property
    def environ(self) -> dict:
        """
        The set of environment variables available to instructions.
        These may be both read and written.
        """
        return self[2]

    @property
    def predefined_symbols(self) -> SymbolTable:
        """
        Symbols that should be available in all steps.

        Should probably not be updated.
        """
        return self[4]


class _ExecutionConfiguration(tuple):
    def __new__(cls,
                configuration: Configuration,
                sandbox_directory_root_name_prefix: str):
        return tuple.__new__(cls, (configuration, sandbox_directory_root_name_prefix))

    @property
    def configuration(self) -> Configuration:
        return self[0]

    @property
    def sandbox_directory_root_name_prefix(self) -> str:
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
            sandbox_directory_root_name_prefix: str,
            is_keep_sandbox: bool) -> PartialResult:
    """
    Takes care of construction of the Sandbox directory structure, including
    the root directory, and executes a given Test Case in this directory.

    Preserves Current Working Directory.

    Perhaps the test case should be executed in a sub process, so that
    Environment Variables and Current Working Directory of the process that executes
    the main program is not modified.

    The responsibility of this method is not the most natural!!
    Please refactor if a more natural responsibility evolves!
    """
    ret_val = None
    try:
        with preserved_cwd():
            exe_configuration = _ExecutionConfiguration(configuration,
                                                        sandbox_directory_root_name_prefix)

            test_case_execution = _PartialExecutor(exe_configuration,
                                                   act_phase_handling,
                                                   test_case,
                                                   initial_setup_settings)
            ret_val = test_case_execution.execute()
            return ret_val
    finally:
        if not is_keep_sandbox:
            if ret_val is not None and ret_val.has_sds:
                shutil.rmtree(str(ret_val.sds.root_dir))


class _PartialExecutor:
    def __init__(self,
                 exe_configuration: _ExecutionConfiguration,
                 act_phase_handling: ActPhaseHandling,
                 test_case: TestCase,
                 setup_settings_builder: SetupSettingsBuilder):
        self.__sandbox_directory_structure = None
        self.__exe_configuration = exe_configuration
        self.__configuration = exe_configuration.configuration
        self.__act_phase_handling = act_phase_handling
        self.__test_case = test_case
        self.__setup_settings_builder = setup_settings_builder
        self.___step_execution_result = _StepExecutionResult()
        self.__source_setup = None
        self.os_services = None
        self.__act_source_and_executor = None
        self.__act_source_and_executor_constructor = act_phase_handling.source_and_executor_constructor
        self.__instruction_environment_pre_sds = InstructionEnvironmentForPreSdsStep(
            self.__configuration.hds,
            self.__configuration.environ,
            self.__configuration.timeout_in_seconds,
            self.__configuration.predefined_symbols.copy())

    def execute(self) -> PartialResult:
        self.__set_pre_sds_environment_variables()
        res = self._sequence([
            self.__act__create_executor_and_parse,
            self.__setup__validate_symbols,
            self.__act__validate_symbols,
            self.__before_assert__validate_symbols,
            self.__assert__validate_symbols,
            self.__cleanup__validate_symbols,
            self.__setup__validate_pre_sds,
            self.__act__validate_pre_sds,
            self.__before_assert__validate_pre_sds,
            self.__assert__validate_pre_sds,
            self.__cleanup__validate_pre_sds,
        ])
        if res.is_failure:
            return res
        self._setup_post_sds_environment()
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
        return new_partial_result_pass(self._sds)

    def _sequence_with_cleanup(self, previous_phase: PreviousPhase, actions: list) -> PartialResult:
        for action in actions:
            res = action()
            if res.is_failure:
                self.__cleanup_main(previous_phase)
                return res
        return new_partial_result_pass(self._sds)

    @property
    def _sds(self) -> SandboxDirectoryStructure:
        return self.__sandbox_directory_structure

    @property
    def exe_configuration(self) -> _ExecutionConfiguration:
        return self.__exe_configuration

    @property
    def configuration(self) -> Configuration:
        return self.__configuration

    def _setup_post_sds_environment(self):
        self.__construct_and_set_sds()
        self.os_services = new_default()
        self.__set_cwd_to_act_dir()
        self.__set_post_sds_environment_variables()
        self.__post_sds_symbol_table = self.__configuration.predefined_symbols.copy()

    def __setup__validate_symbols(self) -> PartialResult:
        return self.__validate_symbols(phase_step.SETUP__VALIDATE_SYMBOLS,
                                       self.__test_case.setup_phase)

    def __before_assert__validate_symbols(self) -> PartialResult:
        return self.__validate_symbols(phase_step.BEFORE_ASSERT__VALIDATE_SYMBOLS,
                                       self.__test_case.before_assert_phase)

    def __assert__validate_symbols(self) -> PartialResult:
        return self.__validate_symbols(phase_step.ASSERT__VALIDATE_SYMBOLS,
                                       self.__test_case.assert_phase)

    def __cleanup__validate_symbols(self) -> PartialResult:
        return self.__validate_symbols(phase_step.CLEANUP__VALIDATE_SYMBOLS,
                                       self.__test_case.cleanup_phase)

    def __setup__validate_pre_sds(self) -> PartialResult:
        return self.__run_instructions_phase_step(phase_step.SETUP__VALIDATE_PRE_SDS,
                                                  phase_step_executors.SetupValidatePreSdsExecutor(
                                                      self.__instruction_environment_pre_sds),
                                                  self.__test_case.setup_phase)

    def __act__create_executor_and_parse(self) -> PartialResult:
        failure_con = _PhaseFailureResultConstructor(phase_step.ACT__PARSE, None)

        def action():
            res = self.__act__create_and_set_executor(phase_step.ACT__PARSE)
            if res.is_failure:
                return res
            try:
                self.__act_source_and_executor.parse(self.__instruction_environment_pre_sds)
            except ParseException as ex:
                return failure_con.apply(PartialResultStatus(PartialResultStatus.VALIDATE),
                                         new_failure_details_from_message(ex.cause.failure_message))
            return new_partial_result_pass(None)

        return self.__execute_action_and_catch_implementation_exception(action,
                                                                        phase_step.ACT__PARSE)

    def __act__validate_symbols(self) -> PartialResult:
        failure_con = _PhaseFailureResultConstructor(phase_step.ACT__VALIDATE_SYMBOLS, None)

        def action():
            executor = phase_step_executors.ValidateSymbolsExecutor(self.__instruction_environment_pre_sds)
            res = executor.apply(self.__act_source_and_executor)
            if res is None:
                return new_partial_result_pass(None)
            else:
                return failure_con.apply(PartialResultStatus(res.status.value),
                                         new_failure_details_from_message(res.error_message))

        return self.__execute_action_and_catch_implementation_exception(action,
                                                                        phase_step.ACT__VALIDATE_SYMBOLS)

    def __act__validate_pre_sds(self) -> PartialResult:
        failure_con = _PhaseFailureResultConstructor(phase_step.ACT__VALIDATE_PRE_SDS, None)

        def action():
            res = self.__act_source_and_executor.validate_pre_sds(self.__instruction_environment_pre_sds)
            if res.is_success:
                return new_partial_result_pass(None)
            else:
                return failure_con.apply(PartialResultStatus(res.status.value),
                                         new_failure_details_from_message(res.failure_message))

        return self.__execute_action_and_catch_implementation_exception(action,
                                                                        phase_step.ACT__VALIDATE_PRE_SDS)

    def __before_assert__validate_pre_sds(self) -> PartialResult:
        return self.__run_instructions_phase_step(
            phase_step.BEFORE_ASSERT__VALIDATE_PRE_SDS,
            phase_step_executors.BeforeAssertValidatePreSdsExecutor(self.__instruction_environment_pre_sds),
            self.__test_case.before_assert_phase)

    def __assert__validate_pre_sds(self) -> PartialResult:
        return self.__run_instructions_phase_step(phase_step.ASSERT__VALIDATE_PRE_SDS,
                                                  phase_step_executors.AssertValidatePreSdsExecutor(
                                                      self.__instruction_environment_pre_sds),
                                                  self.__test_case.assert_phase)

    def __cleanup__validate_pre_sds(self) -> PartialResult:
        return self.__run_instructions_phase_step(phase_step.CLEANUP__VALIDATE_PRE_SDS,
                                                  phase_step_executors.CleanupValidatePreSdsExecutor(
                                                      self.__instruction_environment_pre_sds),
                                                  self.__test_case.cleanup_phase)

    def __setup__main(self) -> PartialResult:
        ret_val = self.__run_instructions_phase_step(phase_step.SETUP__MAIN,
                                                     phase_step_executors.SetupMainExecutor(
                                                         self.os_services,
                                                         self.__post_sds_environment(phase_identifier.SETUP),
                                                         self.__setup_settings_builder),
                                                     self.__test_case.setup_phase)
        self.___step_execution_result.stdin_settings = self.__setup_settings_builder.stdin

        return ret_val

    def __setup__validate_post_setup(self) -> PartialResult:
        return self.__run_instructions_phase_step(phase_step.SETUP__VALIDATE_POST_SETUP,
                                                  phase_step_executors.SetupValidatePostSetupExecutor(
                                                      self.__post_sds_environment(phase_identifier.SETUP)),
                                                  self.__test_case.setup_phase)

    def __act_program_executor(self):
        return _ActProgramExecution(self.__act_source_and_executor,
                                    self.__post_sds_environment(phase_identifier.ACT),
                                    self.___step_execution_result)

    def __before_assert__validate_post_setup(self) -> PartialResult:
        return self.__run_instructions_phase_step(
            phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
            phase_step_executors.BeforeAssertValidatePostSetupExecutor(
                self.__post_sds_environment(phase_identifier.BEFORE_ASSERT)),
            self.__test_case.before_assert_phase)

    def __assert__validate_post_setup(self) -> PartialResult:
        return self.__run_instructions_phase_step(
            phase_step.ASSERT__VALIDATE_POST_SETUP,
            phase_step_executors.AssertValidatePostSetupExecutor(
                self.__post_sds_environment(phase_identifier.ASSERT)),
            self.__test_case.assert_phase)

    def __assert__main(self) -> PartialResult:
        return self.__run_instructions_phase_step(
            phase_step.ASSERT__MAIN,
            phase_step_executors.AssertMainExecutor(
                self.__post_sds_environment(phase_identifier.ASSERT),
                self.os_services),
            self.__test_case.assert_phase)

    def __cleanup_main(self, previous_phase: PreviousPhase) -> PartialResult:
        return self.__run_instructions_phase_step(
            phase_step.CLEANUP__MAIN,
            phase_step_executors.CleanupMainExecutor(
                self.__post_sds_environment(phase_identifier.CLEANUP),
                previous_phase,
                self.os_services),
            self.__test_case.cleanup_phase)

    def __before_assert__main(self) -> PartialResult:
        return self.__run_instructions_phase_step(
            phase_step.BEFORE_ASSERT__MAIN,
            phase_step_executors.BeforeAssertMainExecutor(
                self.__post_sds_environment(phase_identifier.BEFORE_ASSERT),
                self.os_services),
            self.__test_case.before_assert_phase)

    def __validate_symbols(self,
                           step: PhaseStep,
                           phase_contents: SectionContents) -> PartialResult:
        return self.__run_instructions_phase_step(step,
                                                  phase_step_executors.ValidateSymbolsExecutor(
                                                      self.__instruction_environment_pre_sds),
                                                  phase_contents)

    def __set_pre_sds_environment_variables(self):
        self.__configuration.environ.update(
            environment_variables.set_at_setup_pre_validate(self.__configuration.hds))

    def __set_cwd_to_act_dir(self):
        os.chdir(str(self._sds.act_dir))

    def __construct_and_set_sds(self):
        sds_root_dir_name = tempfile.mkdtemp(prefix=self.__exe_configuration.sandbox_directory_root_name_prefix)
        self.__sandbox_directory_structure = construct_at(resolved_path_name(sds_root_dir_name))

    def __post_sds_environment(self,
                               phase: phase_identifier.Phase) -> common.InstructionEnvironmentForPostSdsStep:
        return common.InstructionEnvironmentForPostSdsStep(self.__configuration.hds,
                                                           self.__configuration.environ,
                                                           self.__sandbox_directory_structure,
                                                           phase.identifier,
                                                           timeout_in_seconds=self.__configuration.timeout_in_seconds,
                                                           symbols=self.__post_sds_symbol_table)

    def __set_post_sds_environment_variables(self):
        self.__configuration.environ.update(environment_variables.set_at_setup_main(self._sds))

    def __set_assert_environment_variables(self):
        self.__configuration.environ.update(environment_variables.set_at_assert(self._sds))

    def __run_instructions_phase_step(self,
                                      step: PhaseStep,
                                      instruction_executor: ControlledInstructionExecutor,
                                      phase_contents: SectionContents) -> PartialResult:
        return phase_step_execution.execute_phase(phase_contents,
                                                  phase_step_execution.ElementHeaderExecutorThatDoesNothing(),
                                                  phase_step_execution.ElementHeaderExecutorThatDoesNothing(),
                                                  instruction_executor,
                                                  step,
                                                  self._sds)

    def __act__create_and_set_executor(self, step: PhaseStep) -> PartialResult:
        failure_con = _PhaseFailureResultConstructor(step, None)
        section_contents = self.__test_case.act_phase
        instructions = []
        for element in section_contents.elements:
            if element.element_type is ElementType.INSTRUCTION:
                instruction = element.instruction_info.instruction
                if not isinstance(instruction, ActPhaseInstruction):
                    msg = 'Instruction is not an instance of ' + str(ActPhaseInstruction)
                    return failure_con.implementation_error_msg(msg)
                instructions.append(instruction)
            else:
                msg = 'Act phase contains an element that is not an instruction: ' + str(element.element_type)
                return failure_con.implementation_error_msg(msg)
        self.__act_source_and_executor = self.__act_phase_handling.source_and_executor_constructor.apply(
            self.configuration.act_phase_os_process_executor,
            self.__instruction_environment_pre_sds,
            instructions)
        return new_partial_result_pass(None)

    @staticmethod
    def __execute_action_and_catch_implementation_exception(action_that_returns_partial_result,
                                                            step: PhaseStep) -> PartialResult:
        try:
            return action_that_returns_partial_result()
        except Exception as ex:
            return PartialResult(PartialResultStatus.IMPLEMENTATION_ERROR,
                                 None,
                                 PhaseFailureInfo(step,
                                                  new_failure_details_from_exception(ex)))


class _PhaseFailureResultConstructor:
    def __init__(self,
                 step: PhaseStep,
                 sds: SandboxDirectoryStructure):
        self.step = step
        self.sds = sds

    def apply(self,
              status: PartialResultStatus,
              failure_details: FailureDetails) -> PartialResult:
        return PartialResult(status,
                             self.sds,
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
                 environment: InstructionEnvironmentForPostSdsStep,
                 step_execution_result: _StepExecutionResult()):
        self.act_source_and_executor = act_source_and_executor
        self.environment = environment
        self.home_and_sds = environment.home_and_sds
        self.step_execution_result = step_execution_result
        self.script_output_dir_path = environment.home_and_sds.sds.test_case_dir

    def validate_post_setup(self) -> PartialResult:
        step = phase_step.ACT__VALIDATE_POST_SETUP

        def action():
            res = self.act_source_and_executor.validate_post_setup(self.environment)
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
            res = self.act_source_and_executor.prepare(self.environment,
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

    def _run_act_program_with_opened_stdin_file(self, file_name: pathlib.Path) -> ExitCodeOrHardError:
        try:
            with file_name.open() as f_stdin:
                return self._run_act_program_with_stdin_file(f_stdin)
        except IOError as ex:
            return new_eh_hard_error(new_failure_details_from_exception(
                ex,
                'Failure to open stdin file: ' + str(file_name)))

    def _run_act_program_with_stdin_file(self, f_stdin) -> ExitCodeOrHardError:
        """
        Pre-condition: write has been executed.
        """
        sds = self.home_and_sds.sds
        with open_and_make_read_only_on_close(str(sds.result.stdout_file), 'w') as f_stdout:
            with open_and_make_read_only_on_close(str(sds.result.stderr_file), 'w') as f_stderr:
                exit_code_or_hard_error = self.act_source_and_executor.execute(
                    self.environment,
                    self.script_output_dir_path,
                    StdFiles(f_stdin,
                             StdOutputFiles(f_stdout,
                                            f_stderr)))
                if exit_code_or_hard_error.is_exit_code:
                    self._store_exit_code(exit_code_or_hard_error.exit_code)
                return exit_code_or_hard_error

    def _store_exit_code(self, exitcode: int):
        with open_and_make_read_only_on_close(str(self.home_and_sds.sds.result.exitcode_file), 'w') as f:
            f.write(str(exitcode))

    def _custom_stdin_file_name(self) -> pathlib.Path:
        settings = self.step_execution_result.stdin_settings
        if settings.file_name is not None:
            return settings.file_name
        else:
            file_path = stdin_contents_file(self.home_and_sds.sds)
            write_new_text_file(file_path, settings.contents)
            return file_path

    def _with_implementation_exception_handling(self, step: phase_step.PhaseStep, action) -> PartialResult:
        try:
            return action()
        except Exception as ex:
            return self._failure_con_for(step).implementation_error(ex)

    def _pass(self) -> PartialResult:
        return new_partial_result_pass(self.home_and_sds.sds)

    def _failure_from(self,
                      step: PhaseStep,
                      status: PartialResultStatus,
                      failure_details: FailureDetails) -> PartialResult:
        return self._failure_con_for(step).apply(status, failure_details)

    def _failure_con_for(self, step: PhaseStep) -> _PhaseFailureResultConstructor:
        return _PhaseFailureResultConstructor(step, self.home_and_sds.sds)
