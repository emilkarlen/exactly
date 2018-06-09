import os
import sys
from typing import Sequence, Optional

from exactly_lib.execution import phase_step
from exactly_lib.execution.failure_info import PhaseFailureInfo
from exactly_lib.execution.full_execution.configuration import FullExeInputConfiguration
from exactly_lib.execution.impl import phase_step_executors, phase_step_execution
from exactly_lib.execution.impl.result import PhaseStepFailure, ActionWithFailureAsResult
from exactly_lib.execution.impl.single_instruction_executor import ControlledInstructionExecutor
from exactly_lib.execution.partial_execution.configuration import ConfPhaseValues, TestCase
from exactly_lib.execution.partial_execution.impl.act_phase_execution import PhaseFailureResultConstructor, \
    ActPhaseExecutor
from exactly_lib.execution.partial_execution.result import PartialResultStatus, PartialResult
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
from exactly_lib.util.failure_details import new_failure_details_from_message, new_failure_details_from_exception
from exactly_lib.util.file_utils import resolved_path_name


class ExecutionConfiguration(tuple):
    def __new__(cls,
                conf_from_outside: FullExeInputConfiguration,
                conf_phase_values: ConfPhaseValues,
                setup_settings_builder: SetupSettingsBuilder,
                ):
        return tuple.__new__(cls, (conf_from_outside,
                                   conf_phase_values,
                                   setup_settings_builder))

    @property
    def full_exe_input_conf(self) -> FullExeInputConfiguration:
        return self[0]

    @property
    def conf_phase_values(self) -> ConfPhaseValues:
        return self[1]

    @property
    def setup_settings_builder(self) -> SetupSettingsBuilder:
        return self[2]


def execute(exe_conf: ExecutionConfiguration,
            test_case: TestCase) -> PartialResult:
    executor = _PartialExecutor(exe_conf,
                                test_case)
    return executor.execute()


class _PartialExecutor:
    def __init__(self,
                 exe_conf: ExecutionConfiguration,
                 test_case: TestCase):
        self.__sandbox_directory_structure = None
        self.exe_conf = exe_conf
        self.full_exe_conf = exe_conf.full_exe_input_conf
        self.conf = exe_conf.conf_phase_values
        self.__test_case = test_case
        self.__setup_settings_builder = exe_conf.setup_settings_builder
        self.stdin_conf_from_setup = None
        self.__source_setup = None
        self.os_services = None
        self.__act_source_and_executor = None
        self.__act_source_and_executor_constructor = \
            exe_conf.conf_phase_values.act_phase_handling.source_and_executor_constructor
        self.__instruction_environment_pre_sds = InstructionEnvironmentForPreSdsStep(
            self.conf.hds,
            self.full_exe_conf.environ,
            self.conf.timeout_in_seconds,
            self.full_exe_conf.predefined_symbols.copy())

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
        if res is not None:
            return self._final_failure_result_from(res)
        self._setup_post_sds_environment()

        res = self.__setup__main()
        if res is not None:
            self.__cleanup_main(PreviousPhase.SETUP)
            return self._final_failure_result_from(res)

        act_program_executor = self.__act_program_executor()
        res = self._sequence_with_cleanup(
            PreviousPhase.SETUP,
            [
                self.__setup__validate_post_setup,
                act_program_executor.validate_post_setup,
                self.__before_assert__validate_post_setup,
                self.__assert__validate_post_setup,
                act_program_executor.prepare,
                act_program_executor.execute,
            ])
        if res is not None:
            return self._final_failure_result_from(res)
        self.__set_assert_environment_variables()
        res = self.__before_assert__main()
        if res is not None:
            self.__cleanup_main(PreviousPhase.BEFORE_ASSERT)
            return self._final_failure_result_from(res)

        res_from_assert = self.__assert__main()

        res = self.__cleanup_main(PreviousPhase.ASSERT)
        if res is not None:
            return self._final_failure_result_from(res)
        if res_from_assert is not None:
            return self._final_failure_result_from(res_from_assert)
        return self._final_pass_result()

    def _sequence(self, actions: Sequence[ActionWithFailureAsResult]) -> Optional[PhaseStepFailure]:
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
                self.__cleanup_main(previous_phase)
                return res
        return None

    @property
    def _sds(self) -> SandboxDirectoryStructure:
        return self.__sandbox_directory_structure

    def _setup_post_sds_environment(self):
        self.__construct_and_set_sds()
        self.os_services = new_default()
        self.__set_cwd_to_act_dir()
        self.__set_post_sds_environment_variables()
        self.__post_sds_symbol_table = self.full_exe_conf.predefined_symbols.copy()

    def __setup__validate_symbols(self) -> Optional[PhaseStepFailure]:
        return self.__validate_symbols(phase_step.SETUP__VALIDATE_SYMBOLS,
                                       self.__test_case.setup_phase)

    def __before_assert__validate_symbols(self) -> Optional[PhaseStepFailure]:
        return self.__validate_symbols(phase_step.BEFORE_ASSERT__VALIDATE_SYMBOLS,
                                       self.__test_case.before_assert_phase)

    def __assert__validate_symbols(self) -> Optional[PhaseStepFailure]:
        return self.__validate_symbols(phase_step.ASSERT__VALIDATE_SYMBOLS,
                                       self.__test_case.assert_phase)

    def __cleanup__validate_symbols(self) -> PhaseStepFailure:
        return self.__validate_symbols(phase_step.CLEANUP__VALIDATE_SYMBOLS,
                                       self.__test_case.cleanup_phase)

    def __setup__validate_pre_sds(self) -> Optional[PhaseStepFailure]:
        return self.__run_instructions_phase_step(phase_step.SETUP__VALIDATE_PRE_SDS,
                                                  phase_step_executors.SetupValidatePreSdsExecutor(
                                                      self.__instruction_environment_pre_sds),
                                                  self.__test_case.setup_phase)

    def __act__create_executor_and_parse(self) -> Optional[PhaseStepFailure]:
        failure_con = PhaseFailureResultConstructor(phase_step.ACT__PARSE)

        def action() -> Optional[PhaseStepFailure]:
            res = self.__act__create_and_set_executor(phase_step.ACT__PARSE)
            if res is not None:
                return res
            try:
                self.__act_source_and_executor.parse(self.__instruction_environment_pre_sds)
            except ParseException as ex:
                return failure_con.apply(PartialResultStatus(PartialResultStatus.VALIDATION_ERROR),
                                         new_failure_details_from_message(ex.cause.failure_message))
            return None

        return self.__execute_action_and_catch_implementation_exception(action,
                                                                        phase_step.ACT__PARSE)

    def __act__validate_symbols(self) -> Optional[PhaseStepFailure]:
        failure_con = PhaseFailureResultConstructor(phase_step.ACT__VALIDATE_SYMBOLS)

        def action() -> Optional[PhaseStepFailure]:
            executor = phase_step_executors.ValidateSymbolsExecutor(self.__instruction_environment_pre_sds)
            res = executor.apply(self.__act_source_and_executor)
            if res is None:
                return None
            else:
                return failure_con.apply(PartialResultStatus(res.status.value),
                                         new_failure_details_from_message(res.error_message))

        return self.__execute_action_and_catch_implementation_exception(action,
                                                                        phase_step.ACT__VALIDATE_SYMBOLS)

    def __act__validate_pre_sds(self) -> Optional[PhaseStepFailure]:
        failure_con = PhaseFailureResultConstructor(phase_step.ACT__VALIDATE_PRE_SDS)

        def action() -> Optional[PhaseStepFailure]:
            res = self.__act_source_and_executor.validate_pre_sds(self.__instruction_environment_pre_sds)
            if res.is_success:
                return None
            else:
                return failure_con.apply(PartialResultStatus(res.status.value),
                                         new_failure_details_from_message(res.failure_message))

        return self.__execute_action_and_catch_implementation_exception(action,
                                                                        phase_step.ACT__VALIDATE_PRE_SDS)

    def __before_assert__validate_pre_sds(self) -> Optional[PhaseStepFailure]:
        return self.__run_instructions_phase_step(
            phase_step.BEFORE_ASSERT__VALIDATE_PRE_SDS,
            phase_step_executors.BeforeAssertValidatePreSdsExecutor(self.__instruction_environment_pre_sds),
            self.__test_case.before_assert_phase)

    def __assert__validate_pre_sds(self) -> Optional[PhaseStepFailure]:
        return self.__run_instructions_phase_step(phase_step.ASSERT__VALIDATE_PRE_SDS,
                                                  phase_step_executors.AssertValidatePreSdsExecutor(
                                                      self.__instruction_environment_pre_sds),
                                                  self.__test_case.assert_phase)

    def __cleanup__validate_pre_sds(self) -> Optional[PhaseStepFailure]:
        return self.__run_instructions_phase_step(phase_step.CLEANUP__VALIDATE_PRE_SDS,
                                                  phase_step_executors.CleanupValidatePreSdsExecutor(
                                                      self.__instruction_environment_pre_sds),
                                                  self.__test_case.cleanup_phase)

    def __setup__main(self) -> Optional[PhaseStepFailure]:
        ret_val = self.__run_instructions_phase_step(phase_step.SETUP__MAIN,
                                                     phase_step_executors.SetupMainExecutor(
                                                         self.os_services,
                                                         self.__post_sds_environment(phase_identifier.SETUP),
                                                         self.__setup_settings_builder),
                                                     self.__test_case.setup_phase)
        self.stdin_conf_from_setup = self.__setup_settings_builder.stdin.as_stdin_configuration

        return ret_val

    def __setup__validate_post_setup(self) -> Optional[PhaseStepFailure]:
        return self.__run_instructions_phase_step(phase_step.SETUP__VALIDATE_POST_SETUP,
                                                  phase_step_executors.SetupValidatePostSetupExecutor(
                                                      self.__post_setup_validation_environment(phase_identifier.SETUP)),
                                                  self.__test_case.setup_phase)

    def __act_program_executor(self):
        return ActPhaseExecutor(self.__act_source_and_executor,
                                self.__post_setup_validation_environment(phase_identifier.ACT),
                                self.__post_sds_environment(phase_identifier.ACT),
                                self.stdin_conf_from_setup)

    def __before_assert__validate_post_setup(self) -> Optional[PhaseStepFailure]:
        return self.__run_instructions_phase_step(
            phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
            phase_step_executors.BeforeAssertValidatePostSetupExecutor(
                self.__post_setup_validation_environment(phase_identifier.BEFORE_ASSERT)),
            self.__test_case.before_assert_phase)

    def __assert__validate_post_setup(self) -> Optional[PhaseStepFailure]:
        return self.__run_instructions_phase_step(
            phase_step.ASSERT__VALIDATE_POST_SETUP,
            phase_step_executors.AssertValidatePostSetupExecutor(
                self.__post_setup_validation_environment(phase_identifier.ASSERT)),
            self.__test_case.assert_phase)

    def __assert__main(self) -> Optional[PhaseStepFailure]:
        return self.__run_instructions_phase_step(
            phase_step.ASSERT__MAIN,
            phase_step_executors.AssertMainExecutor(
                self.__post_sds_environment(phase_identifier.ASSERT),
                self.os_services),
            self.__test_case.assert_phase)

    def __cleanup_main(self, previous_phase: PreviousPhase) -> Optional[PhaseStepFailure]:
        return self.__run_instructions_phase_step(
            phase_step.CLEANUP__MAIN,
            phase_step_executors.CleanupMainExecutor(
                self.__post_sds_environment(phase_identifier.CLEANUP),
                previous_phase,
                self.os_services),
            self.__test_case.cleanup_phase)

    def __before_assert__main(self) -> Optional[PhaseStepFailure]:
        return self.__run_instructions_phase_step(
            phase_step.BEFORE_ASSERT__MAIN,
            phase_step_executors.BeforeAssertMainExecutor(
                self.__post_sds_environment(phase_identifier.BEFORE_ASSERT),
                self.os_services),
            self.__test_case.before_assert_phase)

    def __validate_symbols(self,
                           step: PhaseStep,
                           phase_contents: SectionContents) -> Optional[PhaseStepFailure]:
        return self.__run_instructions_phase_step(step,
                                                  phase_step_executors.ValidateSymbolsExecutor(
                                                      self.__instruction_environment_pre_sds),
                                                  phase_contents)

    def __set_pre_sds_environment_variables(self):
        self.full_exe_conf.environ.update(
            environment_variables.set_at_setup_pre_validate(self.conf.hds))

    def __set_cwd_to_act_dir(self):
        os.chdir(str(self._sds.act_dir))

    def __construct_and_set_sds(self):
        sds_root_dir_name = self.exe_conf.full_exe_input_conf.sds_root_dir_resolver()
        self.__sandbox_directory_structure = construct_at(resolved_path_name(sds_root_dir_name))

    def __post_setup_validation_environment(self, phase: phase_identifier.Phase
                                            ) -> common.InstructionEnvironmentForPostSdsStep:
        return common.InstructionEnvironmentForPostSdsStep(self.conf.hds,
                                                           self.full_exe_conf.environ,
                                                           self.__sandbox_directory_structure,
                                                           phase.identifier,
                                                           timeout_in_seconds=self.conf.timeout_in_seconds,
                                                           symbols=self.__instruction_environment_pre_sds.symbols)

    def __post_sds_environment(self,
                               phase: phase_identifier.Phase) -> common.InstructionEnvironmentForPostSdsStep:
        return common.InstructionEnvironmentForPostSdsStep(self.conf.hds,
                                                           self.full_exe_conf.environ,
                                                           self.__sandbox_directory_structure,
                                                           phase.identifier,
                                                           timeout_in_seconds=self.conf.timeout_in_seconds,
                                                           symbols=self.__post_sds_symbol_table)

    def __set_post_sds_environment_variables(self):
        self.full_exe_conf.environ.update(environment_variables.set_at_setup_main(self._sds))

    def __set_assert_environment_variables(self):
        self.full_exe_conf.environ.update(environment_variables.set_at_assert(self._sds))

    def __run_instructions_phase_step(self,
                                      step: PhaseStep,
                                      instruction_executor: ControlledInstructionExecutor,
                                      phase_contents: SectionContents) -> Optional[PhaseStepFailure]:
        return phase_step_execution.execute_phase(phase_contents,
                                                  phase_step_execution.ElementHeaderExecutorThatDoesNothing(),
                                                  phase_step_execution.ElementHeaderExecutorThatDoesNothing(),
                                                  instruction_executor,
                                                  step,
                                                  self._sds)

    def __act__create_and_set_executor(self, step: PhaseStep) -> Optional[PhaseStepFailure]:
        failure_con = PhaseFailureResultConstructor(step)
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
        self.__act_source_and_executor = self.conf.act_phase_handling.source_and_executor_constructor.apply(
            self.full_exe_conf.act_phase_os_process_executor,
            self.__instruction_environment_pre_sds,
            instructions)
        return None

    @staticmethod
    def __execute_action_and_catch_implementation_exception(action: ActionWithFailureAsResult,
                                                            step: PhaseStep) -> Optional[PhaseStepFailure]:
        try:
            return action()
        except Exception as ex:
            return PhaseStepFailure(PartialResultStatus.IMPLEMENTATION_ERROR,
                                    PhaseFailureInfo(step,
                                                     new_failure_details_from_exception(ex, str(sys.exc_info()))))

    def _final_failure_result_from(self, failure: PhaseStepFailure) -> PartialResult:
        return PartialResult(failure.status,
                             self.__sandbox_directory_structure,
                             failure.failure_info)

    def _final_pass_result(self) -> PartialResult:
        return PartialResult(PartialResultStatus.PASS,
                             self.__sandbox_directory_structure,
                             None)
