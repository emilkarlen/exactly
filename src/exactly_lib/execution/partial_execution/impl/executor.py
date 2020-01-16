import os
from typing import Sequence, Optional, Tuple

from exactly_lib.execution import phase_step
from exactly_lib.execution.configuration import ExecutionConfiguration
from exactly_lib.execution.impl import phase_step_executors
from exactly_lib.execution.impl.phase_step_execution import PhaseStepFailureResultConstructor, \
    run_instructions_phase_step, execute_action_and_catch_implementation_exception
from exactly_lib.execution.impl.result import ActionThatRaisesPhaseStepFailureException
from exactly_lib.execution.partial_execution.configuration import ConfPhaseValues, TestCase
from exactly_lib.execution.partial_execution.impl.atc_execution import ActionToCheckExecutor
from exactly_lib.execution.partial_execution.impl.atc_parsing import ActionToCheckParser
from exactly_lib.execution.partial_execution.impl.symbol_validation import SymbolsValidator
from exactly_lib.execution.partial_execution.result import PartialExeResult
from exactly_lib.execution.result import ExecutionFailureStatus, PhaseStepFailure, PhaseStepFailureException
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.actor import ActionToCheck, Actor
from exactly_lib.test_case.os_services import new_default
from exactly_lib.test_case.phases import common
from exactly_lib.test_case.phases.cleanup import PreviousPhase
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.setup import SetupSettingsBuilder
from exactly_lib.test_case.result.failure_details import FailureDetails
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure, construct_at
from exactly_lib.util.file_utils import resolved_path_name
from exactly_lib.util.symbol_table import SymbolTable


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


def parse_atc_and_validate_symbols(actor: Actor,
                                   predefined_symbols: SymbolTable,
                                   test_case: TestCase,
                                   ) -> Tuple[ActionToCheck, SymbolTable]:
    """
    :raises PhaseStepFailureException
    """
    action_to_check = ActionToCheckParser(actor).parse(test_case.act_phase)
    symbols_validator = SymbolsValidator(predefined_symbols,
                                         test_case,
                                         action_to_check
                                         )
    symbols_validator.validate()

    return action_to_check, symbols_validator.output


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
        self._act_phase_executor = None
        self._action_to_check = None
        self._instruction_environment_pre_sds = None

        self.__sandbox_directory_structure = None
        self._action_to_check_outcome = None

    def execute(self) -> PartialExeResult:
        try:
            atc, symbols = parse_atc_and_validate_symbols(self.conf_values.actor,
                                                          self.exe_conf.predefined_symbols,
                                                          self._test_case)

            self._setup_pre_sds_environment(atc, symbols)

            self._setup__validate_pre_sds()
            self._act__validate_pre_sds()
            self._before_assert__validate_pre_sds()
            self._assert__validate_pre_sds()
            self._cleanup__validate_pre_sds()
        except PhaseStepFailureException as ex:
            return self._final_failure_result_from(ex.failure)

        self._setup_post_sds_environment()

        try:
            self._sequence_with_cleanup(
                PreviousPhase.SETUP,
                [
                    self._setup__main,
                    self._construct_and_set_act_phase_executor,
                    self._setup__validate_post_setup,
                    self._act__validate_post_setup,
                    self._before_assert__validate_post_setup,
                    self._assert__validate_post_setup,
                    self._act__prepare,
                ])
        except PhaseStepFailureException as ex:
            return self._final_failure_result_from(ex.failure)

        try:
            self._sequence_with_cleanup(
                PreviousPhase.ACT,
                [
                    self._act__execute,
                ])
        except PhaseStepFailureException as ex:
            self._action_to_check_outcome = self._act_phase_executor.action_to_check_outcome
            return self._final_failure_result_from(ex.failure)

        self._action_to_check_outcome = self._act_phase_executor.action_to_check_outcome

        if self.exe_conf.exe_atc_and_skip_assertions is not None:
            return self._finish_with_cleanup_phase(PreviousPhase.ACT, None)
        else:
            return self._continue_from_before_assert()

    def _continue_from_before_assert(self) -> PartialExeResult:
        try:
            self._before_assert__main()
        except PhaseStepFailureException as ex:
            try:
                self._cleanup_main(PreviousPhase.BEFORE_ASSERT)
                return self._final_failure_result_from(ex.failure)
            except PhaseStepFailureException:
                return self._final_failure_result_from(ex.failure)

        res_of_assert = None
        try:
            self._assert__main()
        except PhaseStepFailureException as ex:
            res_of_assert = ex.failure

        return self._finish_with_cleanup_phase(PreviousPhase.ASSERT, res_of_assert)

    def _finish_with_cleanup_phase(self,
                                   previous_phase: PreviousPhase,
                                   failure_from_previous_step: Optional[PhaseStepFailure]) -> PartialExeResult:
        try:
            self._cleanup_main(previous_phase)
        except PhaseStepFailureException as ex:
            return self._final_failure_result_from(ex.failure)

        if failure_from_previous_step is not None:
            return self._final_failure_result_from(failure_from_previous_step)

        return self._final_pass_result()

    def _sequence_with_cleanup(
            self,
            previous_phase: PreviousPhase,
            actions: Sequence[ActionThatRaisesPhaseStepFailureException]):
        """
        :raises PhaseStepFailureException
        """
        for action in actions:
            try:
                action()
            except PhaseStepFailureException as ex:
                self._cleanup_main(previous_phase)
                raise ex

    @property
    def _sds(self) -> SandboxDirectoryStructure:
        return self.__sandbox_directory_structure

    def _setup_pre_sds_environment(self,
                                   atc: ActionToCheck,
                                   symbols: SymbolTable):
        self._action_to_check = atc
        self._instruction_environment_pre_sds = InstructionEnvironmentForPreSdsStep(
            self.conf_values.hds,
            self.exe_conf.environ,
            self.conf_values.timeout_in_seconds,
            symbols)

    def _setup_post_sds_environment(self):
        self._construct_and_set_sds()
        self._os_services = new_default()
        self._set_cwd_to_act_dir()
        self.__post_sds_symbol_table = self.exe_conf.predefined_symbols.copy()

    def _do_validate_symbols(self) -> SymbolTable:
        symbols_validator = SymbolsValidator(self.exe_conf.predefined_symbols,
                                             self._test_case,
                                             self._action_to_check
                                             )
        symbols_validator.validate()

        return symbols_validator.output

    def _setup__validate_pre_sds(self):
        run_instructions_phase_step(phase_step.SETUP__VALIDATE_PRE_SDS,
                                    phase_step_executors.SetupValidatePreSdsExecutor(
                                        self._instruction_environment_pre_sds),
                                    self._test_case.setup_phase)

    def _construct_and_set_act_phase_executor(self):
        self._act_phase_executor = self._construct_act_phase_executor()

    def _act__parse_atc_executor(self):
        self._action_to_check = ActionToCheckParser(self.conf_values.actor).parse(self._test_case.act_phase)

    def _act__validate_pre_sds(self):
        failure_con = PhaseStepFailureResultConstructor(phase_step.ACT__VALIDATE_PRE_SDS)

        def action():
            res = self._action_to_check.validate_pre_sds(self._instruction_environment_pre_sds)
            if not res.is_success:
                raise PhaseStepFailureException(
                    failure_con.apply(ExecutionFailureStatus(res.status.value),
                                      FailureDetails.new_message(res.failure_message))
                )

        execute_action_and_catch_implementation_exception(action, failure_con)

    def _act__validate_post_setup(self):
        failure_con = PhaseStepFailureResultConstructor(phase_step.ACT__VALIDATE_POST_SETUP)

        execute_action_and_catch_implementation_exception(
            self._act_phase_executor.validate_post_setup(failure_con.apply), failure_con)

    def _act__prepare(self):
        failure_con = PhaseStepFailureResultConstructor(phase_step.ACT__PREPARE)

        execute_action_and_catch_implementation_exception(
            self._act_phase_executor.prepare(failure_con.apply),
            failure_con
        )

    def _act__execute(self):
        failure_con = PhaseStepFailureResultConstructor(phase_step.ACT__EXECUTE)

        return execute_action_and_catch_implementation_exception(
            self._act_phase_executor.execute(failure_con.apply), failure_con)

    def _before_assert__validate_pre_sds(self):
        run_instructions_phase_step(
            phase_step.BEFORE_ASSERT__VALIDATE_PRE_SDS,
            phase_step_executors.BeforeAssertValidatePreSdsExecutor(self._instruction_environment_pre_sds),
            self._test_case.before_assert_phase)

    def _assert__validate_pre_sds(self):
        run_instructions_phase_step(phase_step.ASSERT__VALIDATE_PRE_SDS,
                                    phase_step_executors.AssertValidatePreSdsExecutor(
                                        self._instruction_environment_pre_sds),
                                    self._test_case.assert_phase)

    def _cleanup__validate_pre_sds(self):
        run_instructions_phase_step(phase_step.CLEANUP__VALIDATE_PRE_SDS,
                                    phase_step_executors.CleanupValidatePreSdsExecutor(
                                        self._instruction_environment_pre_sds),
                                    self._test_case.cleanup_phase)

    def _setup__main(self):
        try:
            run_instructions_phase_step(phase_step.SETUP__MAIN,
                                        phase_step_executors.SetupMainExecutor(
                                            self._os_services,
                                            self._post_sds_environment(phase_identifier.SETUP),
                                            self._setup_settings_builder),
                                        self._test_case.setup_phase)
        finally:
            self._stdin_conf_from_setup = self._setup_settings_builder.stdin.as_stdin_configuration

    def _setup__validate_post_setup(self):
        run_instructions_phase_step(phase_step.SETUP__VALIDATE_POST_SETUP,
                                    phase_step_executors.SetupValidatePostSetupExecutor(
                                        self._post_setup_validation_environment(phase_identifier.SETUP)),
                                    self._test_case.setup_phase)

    def _construct_act_phase_executor(self) -> ActionToCheckExecutor:
        return ActionToCheckExecutor(self._action_to_check,
                                     self._post_setup_validation_environment(phase_identifier.ACT),
                                     self._post_sds_environment(phase_identifier.ACT),
                                     self.exe_conf.atc_os_process_executor,
                                     self._stdin_conf_from_setup,
                                     self.exe_conf.exe_atc_and_skip_assertions)

    def _before_assert__validate_post_setup(self):
        run_instructions_phase_step(
            phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
            phase_step_executors.BeforeAssertValidatePostSetupExecutor(
                self._post_setup_validation_environment(phase_identifier.BEFORE_ASSERT)),
            self._test_case.before_assert_phase)

    def _assert__validate_post_setup(self):
        run_instructions_phase_step(
            phase_step.ASSERT__VALIDATE_POST_SETUP,
            phase_step_executors.AssertValidatePostSetupExecutor(
                self._post_setup_validation_environment(phase_identifier.ASSERT)),
            self._test_case.assert_phase)

    def _assert__main(self):
        run_instructions_phase_step(
            phase_step.ASSERT__MAIN,
            phase_step_executors.AssertMainExecutor(
                self._post_sds_environment(phase_identifier.ASSERT),
                self._os_services),
            self._test_case.assert_phase)

    def _cleanup_main(self, previous_phase: PreviousPhase):
        run_instructions_phase_step(
            phase_step.CLEANUP__MAIN,
            phase_step_executors.CleanupMainExecutor(
                self._post_sds_environment(phase_identifier.CLEANUP),
                previous_phase,
                self._os_services),
            self._test_case.cleanup_phase)

    def _before_assert__main(self):
        run_instructions_phase_step(
            phase_step.BEFORE_ASSERT__MAIN,
            phase_step_executors.BeforeAssertMainExecutor(
                self._post_sds_environment(phase_identifier.BEFORE_ASSERT),
                self._os_services),
            self._test_case.before_assert_phase)

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

    def _final_failure_result_from(self, failure: PhaseStepFailure) -> PartialExeResult:
        return PartialExeResult(failure.status,
                                self.__sandbox_directory_structure,
                                self._action_to_check_outcome,
                                failure.failure_info)

    def _final_pass_result(self) -> PartialExeResult:
        return PartialExeResult(None,
                                self.__sandbox_directory_structure,
                                self._action_to_check_outcome,
                                None)
