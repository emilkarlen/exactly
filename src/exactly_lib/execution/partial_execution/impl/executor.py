import os
from typing import Sequence, Optional

from exactly_lib.execution import phase_step
from exactly_lib.execution.configuration import ExecutionConfiguration
from exactly_lib.execution.failure_info import PhaseFailureInfo
from exactly_lib.execution.impl import phase_step_executors, phase_step_execution
from exactly_lib.execution.impl.result import PhaseStepFailure, ActionWithFailureAsResult
from exactly_lib.execution.impl.single_instruction_executor import ControlledInstructionExecutor
from exactly_lib.execution.partial_execution.configuration import ConfPhaseValues, TestCase
from exactly_lib.execution.partial_execution.impl.act_phase_execution import ActPhaseExecutor
from exactly_lib.execution.partial_execution.result import PartialExeResultStatus, PartialExeResult
from exactly_lib.execution.phase_step import PhaseStep
from exactly_lib.section_document.model import SectionContents, ElementType
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.act_phase_handling import ParseException
from exactly_lib.test_case.os_services import new_default
from exactly_lib.test_case.phases import common
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.cleanup import PreviousPhase
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.setup import SetupSettingsBuilder
from exactly_lib.test_case_file_structure import environment_variables
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure, construct_at
from exactly_lib.util.failure_details import new_failure_details_from_message, new_failure_details_from_exception, \
    FailureDetails
from exactly_lib.util.file_utils import resolved_path_name


class Configuration(tuple):
    def __new__(cls,
                conf_from_outside: ExecutionConfiguration,
                conf_phase_values: ConfPhaseValues,
                setup_settings_builder: SetupSettingsBuilder,
                ):
        return tuple.__new__(cls, (conf_from_outside,
                                   conf_phase_values,
                                   setup_settings_builder))

    @property
    def exe_conf(self) -> ExecutionConfiguration:
        return self[0]

    @property
    def conf_phase_values(self) -> ConfPhaseValues:
        return self[1]

    @property
    def setup_settings_builder(self) -> SetupSettingsBuilder:
        return self[2]


def execute(exe_conf: Configuration,
            test_case: TestCase) -> PartialExeResult:
    executor = _PartialExecutor(exe_conf,
                                test_case)
    return executor.execute()


class _PhaseStepFailureResultConstructor:
    def __init__(self, step: PhaseStep):
        self.step = step

    def apply(self,
              status: PartialExeResultStatus,
              failure_details: FailureDetails) -> PhaseStepFailure:
        return PhaseStepFailure(status,
                                PhaseFailureInfo(self.step,
                                                 failure_details))

    def implementation_error(self, ex: Exception) -> PhaseStepFailure:
        return self.apply(PartialExeResultStatus.IMPLEMENTATION_ERROR,
                          new_failure_details_from_exception(ex))

    def implementation_error_msg(self, msg: str) -> PhaseStepFailure:
        return self.apply(PartialExeResultStatus.IMPLEMENTATION_ERROR,
                          new_failure_details_from_message(msg))


class _PartialExecutor:
    def __init__(self,
                 conf: Configuration,
                 test_case: TestCase):
        self.conf = conf
        self.exe_conf = conf.exe_conf
        self.conf_values = conf.conf_phase_values
        self._test_case = test_case
        self._setup_settings_builder = conf.setup_settings_builder
        self._stdin_conf_from_setup = None
        self._source_setup = None
        self._os_services = None
        self._act_program_executor = None
        self._act_source_and_executor = None
        self._act_source_and_executor_constructor = \
            conf.conf_phase_values.act_phase_handling.source_and_executor_constructor
        self._instruction_environment_pre_sds = InstructionEnvironmentForPreSdsStep(
            self.conf_values.hds,
            self.exe_conf.environ,
            self.conf_values.timeout_in_seconds,
            self.exe_conf.predefined_symbols.copy())

        self.__sandbox_directory_structure = None
        self._action_to_check_outcome = None

    def execute(self) -> PartialExeResult:
        self._set_pre_sds_environment_variables()
        res = self._sequence([
            self._act__create_executor_and_parse,
            self._setup__validate_symbols,
            self._act__validate_symbols,
            self._before_assert__validate_symbols,
            self._assert__validate_symbols,
            self._cleanup__validate_symbols,
            self._setup__validate_pre_sds,
            self._act__validate_pre_sds,
            self._before_assert__validate_pre_sds,
            self._assert__validate_pre_sds,
            self._cleanup__validate_pre_sds,
        ])
        if res is not None:
            return self._final_failure_result_from(res)
        self._setup_post_sds_environment()

        res = self._setup__main()
        if res is not None:
            self._cleanup_main(PreviousPhase.SETUP)
            return self._final_failure_result_from(res)

        self._act_program_executor = self._construct_act_program_executor()
        res = self._sequence_with_cleanup(
            PreviousPhase.SETUP,
            [
                self._setup__validate_post_setup,
                self._act__validate_post_setup,
                self._before_assert__validate_post_setup,
                self._assert__validate_post_setup,
                self._act__prepare,
            ])
        if res is not None:
            return self._final_failure_result_from(res)

        res = self._sequence_with_cleanup(
            PreviousPhase.ACT,
            [
                self._act__execute,
            ])
        self._action_to_check_outcome = self._act_program_executor.action_to_check_outcome

        if res is not None:
            return self._final_failure_result_from(res)

        if self.exe_conf.exe_atc_and_skip_assertions is not None:
            return self._finish_with_cleanup_phase(PreviousPhase.ACT, None)
        else:
            return self._continue_from_before_assert()

    def _continue_from_before_assert(self) -> PartialExeResult:
        self._set_assert_environment_variables()
        res = self._before_assert__main()
        if res is not None:
            self._cleanup_main(PreviousPhase.BEFORE_ASSERT)
            return self._final_failure_result_from(res)

        res_from_assert = self._assert__main()

        return self._finish_with_cleanup_phase(PreviousPhase.ASSERT, res_from_assert)

    def _finish_with_cleanup_phase(self,
                                   previous_phase: PreviousPhase,
                                   failure_from_previous_step: Optional[PhaseStepFailure]) -> PartialExeResult:
        res = self._cleanup_main(previous_phase)
        if res is not None:
            return self._final_failure_result_from(res)
        if failure_from_previous_step is not None:
            return self._final_failure_result_from(failure_from_previous_step)
        return self._final_pass_result()

    @staticmethod
    def _sequence(actions: Sequence[ActionWithFailureAsResult]) -> Optional[PhaseStepFailure]:
        for action in actions:
            res = action()
            if res is not None:
                return res
        return None

    def _sequence_with_cleanup(
            self,
            previous_phase: PreviousPhase,
            actions: Sequence[ActionWithFailureAsResult]) -> Optional[PhaseStepFailure]:
        for action in actions:
            res = action()
            if res is not None:
                self._cleanup_main(previous_phase)
                return res
        return None

    @property
    def _sds(self) -> SandboxDirectoryStructure:
        return self.__sandbox_directory_structure

    def _setup_post_sds_environment(self):
        self._construct_and_set_sds()
        self._os_services = new_default()
        self._set_cwd_to_act_dir()
        self._set_post_sds_environment_variables()
        self.__post_sds_symbol_table = self.exe_conf.predefined_symbols.copy()

    def _setup__validate_symbols(self) -> Optional[PhaseStepFailure]:
        return self._validate_symbols(phase_step.SETUP__VALIDATE_SYMBOLS,
                                      self._test_case.setup_phase)

    def _before_assert__validate_symbols(self) -> Optional[PhaseStepFailure]:
        return self._validate_symbols(phase_step.BEFORE_ASSERT__VALIDATE_SYMBOLS,
                                      self._test_case.before_assert_phase)

    def _assert__validate_symbols(self) -> Optional[PhaseStepFailure]:
        return self._validate_symbols(phase_step.ASSERT__VALIDATE_SYMBOLS,
                                      self._test_case.assert_phase)

    def _cleanup__validate_symbols(self) -> PhaseStepFailure:
        return self._validate_symbols(phase_step.CLEANUP__VALIDATE_SYMBOLS,
                                      self._test_case.cleanup_phase)

    def _setup__validate_pre_sds(self) -> Optional[PhaseStepFailure]:
        return _run_instructions_phase_step(phase_step.SETUP__VALIDATE_PRE_SDS,
                                            phase_step_executors.SetupValidatePreSdsExecutor(
                                                self._instruction_environment_pre_sds),
                                            self._test_case.setup_phase)

    def _act__create_executor_and_parse(self) -> Optional[PhaseStepFailure]:
        failure_con = _PhaseStepFailureResultConstructor(phase_step.ACT__PARSE)

        def action() -> Optional[PhaseStepFailure]:
            res = self._act__create_and_set_executor(failure_con)
            if res is not None:
                return res
            try:
                self._act_source_and_executor.parse(self._instruction_environment_pre_sds)
            except ParseException as ex:
                return failure_con.apply(PartialExeResultStatus.VALIDATION_ERROR,
                                         new_failure_details_from_message(ex.cause.failure_message))
            return None

        return _execute_action_and_catch_implementation_exception(action, failure_con)

    def _act__validate_symbols(self) -> Optional[PhaseStepFailure]:
        failure_con = _PhaseStepFailureResultConstructor(phase_step.ACT__VALIDATE_SYMBOLS)

        def action() -> Optional[PhaseStepFailure]:
            executor = phase_step_executors.ValidateSymbolsExecutor(self._instruction_environment_pre_sds)
            res = executor.apply(self._act_source_and_executor)
            if res is None:
                return None
            else:
                return failure_con.apply(PartialExeResultStatus(res.status.value),
                                         new_failure_details_from_message(res.error_message))

        return _execute_action_and_catch_implementation_exception(action, failure_con)

    def _act__validate_pre_sds(self) -> Optional[PhaseStepFailure]:
        failure_con = _PhaseStepFailureResultConstructor(phase_step.ACT__VALIDATE_PRE_SDS)

        def action() -> Optional[PhaseStepFailure]:
            res = self._act_source_and_executor.validate_pre_sds(self._instruction_environment_pre_sds)
            if res.is_success:
                return None
            else:
                return failure_con.apply(PartialExeResultStatus(res.status.value),
                                         new_failure_details_from_message(res.failure_message))

        return _execute_action_and_catch_implementation_exception(action, failure_con)

    def _act__validate_post_setup(self) -> Optional[PhaseStepFailure]:
        failure_con = _PhaseStepFailureResultConstructor(phase_step.ACT__VALIDATE_POST_SETUP)

        return _execute_action_and_catch_implementation_exception(
            self._act_program_executor.validate_post_setup(failure_con.apply), failure_con)

    def _act__prepare(self) -> Optional[PhaseStepFailure]:
        failure_con = _PhaseStepFailureResultConstructor(phase_step.ACT__PREPARE)

        return _execute_action_and_catch_implementation_exception(
            self._act_program_executor.prepare(failure_con.apply), failure_con)

    def _act__execute(self) -> Optional[PhaseStepFailure]:
        failure_con = _PhaseStepFailureResultConstructor(phase_step.ACT__EXECUTE)

        return _execute_action_and_catch_implementation_exception(
            self._act_program_executor.execute(failure_con.apply), failure_con)

    def _before_assert__validate_pre_sds(self) -> Optional[PhaseStepFailure]:
        return _run_instructions_phase_step(
            phase_step.BEFORE_ASSERT__VALIDATE_PRE_SDS,
            phase_step_executors.BeforeAssertValidatePreSdsExecutor(self._instruction_environment_pre_sds),
            self._test_case.before_assert_phase)

    def _assert__validate_pre_sds(self) -> Optional[PhaseStepFailure]:
        return _run_instructions_phase_step(phase_step.ASSERT__VALIDATE_PRE_SDS,
                                            phase_step_executors.AssertValidatePreSdsExecutor(
                                                self._instruction_environment_pre_sds),
                                            self._test_case.assert_phase)

    def _cleanup__validate_pre_sds(self) -> Optional[PhaseStepFailure]:
        return _run_instructions_phase_step(phase_step.CLEANUP__VALIDATE_PRE_SDS,
                                            phase_step_executors.CleanupValidatePreSdsExecutor(
                                                self._instruction_environment_pre_sds),
                                            self._test_case.cleanup_phase)

    def _setup__main(self) -> Optional[PhaseStepFailure]:
        ret_val = _run_instructions_phase_step(phase_step.SETUP__MAIN,
                                               phase_step_executors.SetupMainExecutor(
                                                   self._os_services,
                                                   self._post_sds_environment(phase_identifier.SETUP),
                                                   self._setup_settings_builder),
                                               self._test_case.setup_phase)
        self._stdin_conf_from_setup = self._setup_settings_builder.stdin.as_stdin_configuration

        return ret_val

    def _setup__validate_post_setup(self) -> Optional[PhaseStepFailure]:
        return _run_instructions_phase_step(phase_step.SETUP__VALIDATE_POST_SETUP,
                                            phase_step_executors.SetupValidatePostSetupExecutor(
                                                self._post_setup_validation_environment(phase_identifier.SETUP)),
                                            self._test_case.setup_phase)

    def _construct_act_program_executor(self) -> ActPhaseExecutor:
        return ActPhaseExecutor(self._act_source_and_executor,
                                self._post_setup_validation_environment(phase_identifier.ACT),
                                self._post_sds_environment(phase_identifier.ACT),
                                self._stdin_conf_from_setup,
                                self.exe_conf.exe_atc_and_skip_assertions)

    def _before_assert__validate_post_setup(self) -> Optional[PhaseStepFailure]:
        return _run_instructions_phase_step(
            phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
            phase_step_executors.BeforeAssertValidatePostSetupExecutor(
                self._post_setup_validation_environment(phase_identifier.BEFORE_ASSERT)),
            self._test_case.before_assert_phase)

    def _assert__validate_post_setup(self) -> Optional[PhaseStepFailure]:
        return _run_instructions_phase_step(
            phase_step.ASSERT__VALIDATE_POST_SETUP,
            phase_step_executors.AssertValidatePostSetupExecutor(
                self._post_setup_validation_environment(phase_identifier.ASSERT)),
            self._test_case.assert_phase)

    def _assert__main(self) -> Optional[PhaseStepFailure]:
        return _run_instructions_phase_step(
            phase_step.ASSERT__MAIN,
            phase_step_executors.AssertMainExecutor(
                self._post_sds_environment(phase_identifier.ASSERT),
                self._os_services),
            self._test_case.assert_phase)

    def _cleanup_main(self, previous_phase: PreviousPhase) -> Optional[PhaseStepFailure]:
        return _run_instructions_phase_step(
            phase_step.CLEANUP__MAIN,
            phase_step_executors.CleanupMainExecutor(
                self._post_sds_environment(phase_identifier.CLEANUP),
                previous_phase,
                self._os_services),
            self._test_case.cleanup_phase)

    def _before_assert__main(self) -> Optional[PhaseStepFailure]:
        return _run_instructions_phase_step(
            phase_step.BEFORE_ASSERT__MAIN,
            phase_step_executors.BeforeAssertMainExecutor(
                self._post_sds_environment(phase_identifier.BEFORE_ASSERT),
                self._os_services),
            self._test_case.before_assert_phase)

    def _validate_symbols(self,
                          step: PhaseStep,
                          phase_contents: SectionContents) -> Optional[PhaseStepFailure]:
        return _run_instructions_phase_step(step,
                                            phase_step_executors.ValidateSymbolsExecutor(
                                                self._instruction_environment_pre_sds),
                                            phase_contents)

    def _set_pre_sds_environment_variables(self):
        self.exe_conf.environ.update(
            environment_variables.set_at_setup_pre_validate(self.conf_values.hds))

    def _set_cwd_to_act_dir(self):
        os.chdir(str(self._sds.act_dir))

    def _construct_and_set_sds(self):
        sds_root_dir_name = self.conf.exe_conf.sds_root_dir_resolver()
        self.__sandbox_directory_structure = construct_at(resolved_path_name(sds_root_dir_name))

    def _post_setup_validation_environment(self, phase: phase_identifier.Phase
                                           ) -> common.InstructionEnvironmentForPostSdsStep:
        return common.InstructionEnvironmentForPostSdsStep(self.conf_values.hds,
                                                           self.exe_conf.environ,
                                                           self.__sandbox_directory_structure,
                                                           phase.identifier,
                                                           timeout_in_seconds=self.conf_values.timeout_in_seconds,
                                                           symbols=self._instruction_environment_pre_sds.symbols)

    def _post_sds_environment(self,
                              phase: phase_identifier.Phase) -> common.InstructionEnvironmentForPostSdsStep:
        return common.InstructionEnvironmentForPostSdsStep(self.conf_values.hds,
                                                           self.exe_conf.environ,
                                                           self.__sandbox_directory_structure,
                                                           phase.identifier,
                                                           timeout_in_seconds=self.conf_values.timeout_in_seconds,
                                                           symbols=self.__post_sds_symbol_table)

    def _set_post_sds_environment_variables(self):
        self.exe_conf.environ.update(environment_variables.set_at_setup_main(self._sds))

    def _set_assert_environment_variables(self):
        self.exe_conf.environ.update(environment_variables.set_at_assert(self._sds))

    def _act__create_and_set_executor(self, failure_con: _PhaseStepFailureResultConstructor
                                      ) -> Optional[PhaseStepFailure]:
        section_contents = self._test_case.act_phase
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
        self._act_source_and_executor = self.conf_values.act_phase_handling.source_and_executor_constructor.apply(
            self.exe_conf.act_phase_os_process_executor,
            self._instruction_environment_pre_sds,
            instructions)
        return None

    def _final_failure_result_from(self, failure: PhaseStepFailure) -> PartialExeResult:
        return PartialExeResult(failure.status,
                                self.__sandbox_directory_structure,
                                self._action_to_check_outcome,
                                failure.failure_info)

    def _final_pass_result(self) -> PartialExeResult:
        return PartialExeResult(PartialExeResultStatus.PASS,
                                self.__sandbox_directory_structure,
                                self._action_to_check_outcome,
                                None)


def _run_instructions_phase_step(step: PhaseStep,
                                 instruction_executor: ControlledInstructionExecutor,
                                 phase_contents: SectionContents) -> Optional[PhaseStepFailure]:
    return phase_step_execution.execute_phase(phase_contents,
                                              phase_step_execution.ElementHeaderExecutorThatDoesNothing(),
                                              phase_step_execution.ElementHeaderExecutorThatDoesNothing(),
                                              instruction_executor,
                                              step)


def _execute_action_and_catch_implementation_exception(action: ActionWithFailureAsResult,
                                                       failure_con: _PhaseStepFailureResultConstructor
                                                       ) -> Optional[PhaseStepFailure]:
    try:
        return action()
    except Exception as ex:
        return failure_con.implementation_error(ex)
