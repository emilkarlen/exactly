import os
import unittest
from contextlib import contextmanager
from typing import List, Optional, Sequence, ContextManager, Callable

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.execution import phase_step
from exactly_lib.impls.types.string_source.factory import RootStringSourceFactory
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.act.actor import Actor, ActionToCheck
from exactly_lib.test_case.phases.act.execution_input import ActExecutionInput
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result import svh, sh
from exactly_lib.test_case.result.eh import ExitCodeOrHardError, new_eh_exit_code
from exactly_lib.test_case.result.failure_details import FailureDetails
from exactly_lib.util.file_utils.std import StdFiles, StdOutputFiles
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.execution.test_resources import eh_assertions as asrt_eh
from exactly_lib_test.impls.test_resources.validation.svh_validation import ValidationExpectationSvh
from exactly_lib_test.tcfs.test_resources import hds_populators
from exactly_lib_test.tcfs.test_resources.ds_action import PlainTcdsAction
from exactly_lib_test.tcfs.test_resources.hds_utils import home_directory_structure
from exactly_lib_test.test_case.result.test_resources import failure_details_assertions as asrt_failure_details, \
    sh_assertions as asrt_sh
from exactly_lib_test.test_case.result.test_resources import sh_assertions
from exactly_lib_test.test_case.test_resources.arrangements import ProcessExecutionArrangement
from exactly_lib_test.test_case.test_resources.instruction_environment import InstructionEnvironmentPostSdsBuilder
from exactly_lib_test.test_resources.process import SubProcessResult, ProcessExecutor, \
    capture_process_executor_result__wo_stdin, ProcessExecutorWoStdin
from exactly_lib_test.test_resources.tcds_and_symbols.sds_env_utils import sds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder, ValueAssertion
from exactly_lib_test.util.process_execution.test_resources.proc_exe_env import proc_exe_env_for_test


class HardErrorResultError(Exception):
    def __init__(self,
                 result: ExitCodeOrHardError,
                 failure_details: FailureDetails):
        self.result = result
        self.failure_details = failure_details


class Arrangement:
    def __init__(self,
                 hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
                 symbol_table: Optional[SymbolTable] = None,
                 process_execution: ProcessExecutionArrangement = ProcessExecutionArrangement(
                     process_execution_settings=proc_exe_env_for_test()
                 ),
                 stdin_contents: str = '',
                 post_sds_action: PlainTcdsAction = PlainTcdsAction(),
                 mem_buff_size: int = 2 ** 10,
                 ):
        self.symbol_table = symbol_table_from_none_or_value(symbol_table)
        self.hds_contents = hds_contents
        self.process_execution = process_execution
        self.stdin_contents = stdin_contents
        self.post_sds_action = post_sds_action
        self.mem_buff_size = mem_buff_size

    @property
    def proc_exe_settings(self) -> ProcessExecutionSettings:
        return self.process_execution.process_execution_settings


class PostSdsExpectation:
    def __init__(self,
                 side_effects_on_files_after_prepare: ValueAssertion[SandboxDs]
                 = asrt.anything_goes(),
                 side_effects_on_files_after_execute: ValueAssertion[SandboxDs]
                 = asrt.anything_goes(),
                 sub_process_result_from_execute: ValueAssertion[SubProcessResult] = asrt.anything_goes(),
                 ):
        self.side_effects_on_files_after_prepare = side_effects_on_files_after_prepare
        self.side_effects_on_files_after_execute = side_effects_on_files_after_execute
        self.sub_process_result_from_execute = sub_process_result_from_execute

    @staticmethod
    def constant(
            side_effects_on_files_after_prepare: ValueAssertion[SandboxDs]
            = asrt.anything_goes(),
            side_effects_on_files_after_execute: ValueAssertion[SandboxDs]
            = asrt.anything_goes(),
            sub_process_result_from_execute: ValueAssertion[SubProcessResult] = asrt.anything_goes(),
    ) -> Callable[[SandboxDs], 'PostSdsExpectation']:
        def ret_val(sds: SandboxDs) -> 'PostSdsExpectation':
            return PostSdsExpectation(
                side_effects_on_files_after_prepare,
                side_effects_on_files_after_execute,
                sub_process_result_from_execute,
            )

        return ret_val


class Expectation:
    def __init__(self,
                 validation: ValidationExpectationSvh
                 = ValidationExpectationSvh.passes(),
                 prepare: ValueAssertion[sh.SuccessOrHardError]
                 = sh_assertions.is_success(),
                 execute: ValueAssertion[ExitCodeOrHardError]
                 = asrt_eh.is_any_exit_code,
                 symbol_usages: ValueAssertion[Sequence[SymbolUsage]]
                 = asrt.is_empty_sequence,
                 post_sds: Callable[[SandboxDs], PostSdsExpectation] =
                 lambda sds: PostSdsExpectation(),
                 after_execution: ValueAssertion[TestCaseDs] =
                 asrt.anything_goes(),
                 ):
        self.symbol_usages = symbol_usages
        self.validation = validation
        self.prepare = prepare
        self.execute = execute
        self.post_sds = post_sds
        self.after_execution = after_execution

    @staticmethod
    def hard_error_from_prepare(
            error_message: ValueAssertion[TextRenderer] = asrt_text_doc.is_any_text(),
            symbol_usages: ValueAssertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
    ) -> 'Expectation':
        return Expectation(
            symbol_usages=symbol_usages,
            prepare=asrt_sh.is_hard_error(error_message)
        )

    @staticmethod
    def hard_error_from_execute(
            error_message: ValueAssertion[TextRenderer] = asrt_text_doc.is_any_text(),
            symbol_usages: ValueAssertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
    ) -> 'Expectation':
        return Expectation(
            symbol_usages=symbol_usages,
            execute=asrt_eh.matches_hard_error(asrt_failure_details.is_failure_message_matching__td(
                error_message
            )
            )
        )


def simple_success() -> Expectation:
    return Expectation()


def check_execution(put: unittest.TestCase,
                    actor: Actor,
                    act_phase_instructions: List[ActPhaseInstruction],
                    arrangement: Arrangement,
                    expectation: Expectation,
                    ):
    checker = _Checker(put, actor, act_phase_instructions, arrangement, expectation)
    checker.check()


class ProcessExecutorForProgramExecutorThatRaisesIfResultIsNotExitCode(ProcessExecutor):
    """
    An executor that raises HardErrorResultError if result is not an exit code.
    """

    def __init__(self,
                 environment: InstructionEnvironmentForPostSdsStep,
                 os_services: OsServices,
                 atc: ActionToCheck):
        self.environment = environment
        self.os_services = os_services
        self.atc = atc

    def execute(self, files: StdFiles) -> int:
        """
         :raises HardErrorResultError: Return value from executor is not an exit code.
        """
        exit_code_or_hard_error = self.atc.execute(self.environment, self.os_services, files)
        if exit_code_or_hard_error.is_exit_code:
            return exit_code_or_hard_error.exit_code
        raise HardErrorResultError(exit_code_or_hard_error,
                                   exit_code_or_hard_error.failure_details)


class _Checker:
    def __init__(self,
                 put: unittest.TestCase,
                 actor: Actor,
                 instructions: List[ActPhaseInstruction],
                 arrangement: Arrangement,
                 expectation: Expectation,
                 ):
        self._actor = actor
        self._instructions = instructions
        self._put = put
        self._arrangement = arrangement
        self._expectation = expectation

        self.hds = None
        self.tcds = None
        self._expectation_post_sds = None

    def check(self):
        try:
            self._check()
        except _CheckIsDoneException:
            return None

    def _check(self):
        atc = self._parse()
        with self._pre_sds_env() as env_pre_sds:
            self._validate_pre_sds(atc, env_pre_sds)

            with self._post_sds_env(env_pre_sds) as env_post_sds:
                self._validate_post_sds(atc, env_post_sds)
                self._prepare(atc, env_post_sds)
                self._execute(atc, env_post_sds)

    def _parse(self) -> ActionToCheck:
        atc = self._actor.parse(self._instructions)
        self._check_symbols_after(atc, phase_step.STEP__ACT__PARSE)

        return atc

    @contextmanager
    def _pre_sds_env(self) -> ContextManager[InstructionEnvironmentForPreSdsStep]:
        with home_directory_structure(contents=self._arrangement.hds_contents) as hds:
            instruction_environment = InstructionEnvironmentForPreSdsStep(
                hds,
                self._arrangement.proc_exe_settings,
                self._arrangement.symbol_table,
                self._arrangement.mem_buff_size)
            yield instruction_environment

    @contextmanager
    def _post_sds_env(self, env_pre_sds: InstructionEnvironmentForPreSdsStep,
                      ) -> ContextManager[InstructionEnvironmentForPostSdsStep]:
        with sds_with_act_as_curr_dir(symbols=env_pre_sds.symbols
                                      ) as path_resolving_env:
            environment_builder = InstructionEnvironmentPostSdsBuilder.new_from_pre_sds(
                env_pre_sds,
                path_resolving_env.sds,
            )
            env_post_sds = environment_builder.build_post_sds()
            self._arrangement.post_sds_action.apply(env_post_sds.tcds)
            self._expectation_post_sds = self._expectation.post_sds(env_post_sds.sds)
            yield env_post_sds

    def _validate_pre_sds(self,
                          atc: ActionToCheck,
                          env: InstructionEnvironmentForPreSdsStep,
                          ):
        step_result = atc.validate_pre_sds(env)
        self._expectation.validation.pre_sds.apply_with_message(
            self._put,
            step_result,
            phase_step.STEP__VALIDATE_PRE_SDS,
        )
        self._check_symbols_after(atc, phase_step.STEP__VALIDATE_PRE_SDS)

        if step_result.status is not svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS:
            raise _CheckIsDoneException()

    def _validate_post_sds(self,
                           atc: ActionToCheck,
                           env: InstructionEnvironmentForPostSdsStep,
                           ):
        step_result = atc.validate_post_setup(env)
        self._expectation.validation.post_sds.apply_with_message(
            self._put,
            step_result,
            phase_step.STEP__VALIDATE_POST_SETUP,
        )
        self._check_symbols_after(atc, phase_step.STEP__VALIDATE_POST_SETUP)

        if step_result.status is not svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS:
            raise _CheckIsDoneException()

    def _prepare(self,
                 atc: ActionToCheck,
                 env: InstructionEnvironmentForPostSdsStep,
                 ):
        step_result = atc.prepare(env,
                                  self._arrangement.process_execution.os_services)
        self._expectation_post_sds.side_effects_on_files_after_prepare.apply(self._put, env.sds)
        self._expectation.prepare.apply(self._put,
                                        step_result,
                                        MessageBuilder('Result of prepare'))
        self._check_symbols_after(atc, phase_step.STEP__ACT__PREPARE)
        if not step_result.is_success:
            raise _CheckIsDoneException()

    def _execute(self,
                 atc: ActionToCheck,
                 env: InstructionEnvironmentForPostSdsStep,
                 ):
        process_executor = ProcessExecutorForProgramExecutorWoStdinThatRaisesIfResultIsNotExitCode(
            env,
            self._arrangement.process_execution.os_services,
            atc,
            self._act_exe_input(env)
        )
        error_msg_extra_info = ''
        sub_process_result = None
        try:
            sub_process_result = capture_process_executor_result__wo_stdin(process_executor,
                                                                           env.sds.result.root_dir)
            step_result = new_eh_exit_code(sub_process_result.exitcode)
        except HardErrorResultError as ex:
            step_result = ex.result
            error_msg_extra_info = os.linesep + str(ex.failure_details) + os.linesep

        self._expectation.execute.apply(self._put,
                                        step_result,
                                        MessageBuilder('Result of execute' + error_msg_extra_info))
        if sub_process_result:
            msg_builder = MessageBuilder('Sub process output from execute ' + error_msg_extra_info)
            self._expectation_post_sds.sub_process_result_from_execute.apply(self._put, sub_process_result, msg_builder)

        self._expectation_post_sds.side_effects_on_files_after_execute.apply(self._put, env.sds)
        self._check_symbols_after(atc, phase_step.STEP__ACT__EXECUTE)
        self._expectation.after_execution.apply_with_message(self._put, env.tcds, 'after execution')

    def _act_exe_input(self, env: InstructionEnvironmentForPostSdsStep) -> ActExecutionInput:
        stdin_contents = self._arrangement.stdin_contents
        if stdin_contents is None or not stdin_contents:
            return ActExecutionInput.empty()
        else:
            model_factory = RootStringSourceFactory(env.tmp_dir__path_access.paths_access)
            return ActExecutionInput(model_factory.of_const_str(stdin_contents))

    def _check_symbols_after(self, atc: ActionToCheck, step: str):
        self._expectation.symbol_usages.apply_with_message(
            self._put,
            atc.symbol_usages(),
            'symbol-usages after ' + step)


class _CheckIsDoneException(Exception):
    pass


class ProcessExecutorForProgramExecutorWoStdinThatRaisesIfResultIsNotExitCode(ProcessExecutorWoStdin):
    """
    An executor that raises HardErrorResultError if result is not an exit code.
    """

    def __init__(self,
                 environment: InstructionEnvironmentForPostSdsStep,
                 os_services: OsServices,
                 atc: ActionToCheck,
                 input_: ActExecutionInput,
                 ):
        self.environment = environment
        self.os_services = os_services
        self.atc = atc
        self.input_ = input_

    def execute(self, output: StdOutputFiles) -> int:
        """
         :raises HardErrorResultError: Return value from executor is not an exit code.
        """
        exit_code_or_hard_error = self.atc.execute(self.environment, self.os_services, self.input_, output)
        if exit_code_or_hard_error.is_exit_code:
            return exit_code_or_hard_error.exit_code
        raise HardErrorResultError(exit_code_or_hard_error,
                                   exit_code_or_hard_error.failure_details)
