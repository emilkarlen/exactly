import os
import unittest
from typing import List, Optional, Sequence, Callable

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
from exactly_lib_test.tcfs.test_resources.ds_construction import TcdsArrangementPreAct, \
    tcds_with_act_as_curr_dir__pre_act__optional
from exactly_lib_test.test_case.result.test_resources import failure_details_assertions as asrt_failure_details, \
    sh_assertions as asrt_sh
from exactly_lib_test.test_case.result.test_resources import sh_assertions
from exactly_lib_test.test_case.test_resources import act_phase_instruction
from exactly_lib_test.test_case.test_resources.arrangements import ProcessExecutionArrangement
from exactly_lib_test.test_case.test_resources.instruction_environment import InstructionEnvironmentPostSdsBuilder
from exactly_lib_test.test_resources.process import SubProcessResult, ProcessExecutor, \
    capture_process_executor_result__wo_stdin, ProcessExecutorWoStdin
from exactly_lib_test.test_resources.source import layout
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder, ValueAssertion, \
    StopAssertion
from exactly_lib_test.util.process_execution.test_resources.proc_exe_env import proc_exe_env_for_test


class HardErrorResultError(Exception):
    def __init__(self,
                 result: ExitCodeOrHardError,
                 failure_details: FailureDetails):
        self.result = result
        self.failure_details = failure_details


class Arrangement:
    def __init__(self,
                 tcds: Optional[TcdsArrangementPreAct] = None,
                 symbols: Optional[SymbolTable] = None,
                 process_execution: ProcessExecutionArrangement = ProcessExecutionArrangement(
                     process_execution_settings=proc_exe_env_for_test()
                 ),
                 stdin_contents: str = '',
                 mem_buff_size: int = 2 ** 10,
                 ):
        self.symbol_table = symbol_table_from_none_or_value(symbols)
        self.tcds = tcds
        self.process_execution = process_execution
        self.stdin_contents = stdin_contents
        self.mem_buff_size = mem_buff_size

    @property
    def proc_exe_settings(self) -> ProcessExecutionSettings:
        return self.process_execution.process_execution_settings


def arrangement_w_tcds(
        hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
        symbol_table: Optional[SymbolTable] = None,
        process_execution: ProcessExecutionArrangement = ProcessExecutionArrangement(
            process_execution_settings=proc_exe_env_for_test()
        ),
        stdin_contents: str = '',
        post_sds_action: PlainTcdsAction = PlainTcdsAction(),
        mem_buff_size: int = 2 ** 10,
) -> Arrangement:
    return Arrangement(
        tcds=TcdsArrangementPreAct(
            hds_contents=hds_contents,
            post_population_action=post_sds_action,
        ),
        symbols=symbol_table,
        process_execution=process_execution,
        stdin_contents=stdin_contents,
        mem_buff_size=mem_buff_size,
    )


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
    checker = _Executor(put, actor, act_phase_instructions, arrangement, expectation)
    checker.check()


class Checker:
    def __init__(self, actor: Actor):
        self._actor = actor

    def check(self,
              put: unittest.TestCase,
              instructions: List[ActPhaseInstruction],
              arrangement: Arrangement,
              expectation: Expectation,
              ):
        executor = _Executor(put, self._actor, instructions, arrangement, expectation)
        executor.check()

    def check__abs_stx(self,
                       put: unittest.TestCase,
                       syntax: AbstractSyntax,
                       arrangement: Arrangement,
                       expectation: Expectation,
                       ):
        for layout_spec in layout.STANDARD_LAYOUT_SPECS:
            source_str = syntax.tokenization().layout(layout_spec.value)
            source_lines = source_str.splitlines(keepends=False)
            with put.subTest(layout=layout_spec.name):
                self.check(
                    put,
                    [act_phase_instruction.instr(source_lines)],
                    arrangement,
                    expectation,
                )


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


class _Executor:
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
        except StopAssertion:
            return None

    def _check(self):
        atc = self._parse()
        with tcds_with_act_as_curr_dir__pre_act__optional(self._arrangement.tcds) as tcds:
            env_pre_sds = InstructionEnvironmentForPreSdsStep(
                tcds.hds,
                self._arrangement.proc_exe_settings,
                self._arrangement.symbol_table,
                self._arrangement.mem_buff_size,
            )

            self._check_pre_sds(atc, env_pre_sds)

            environment_builder = InstructionEnvironmentPostSdsBuilder.new_from_pre_sds(
                env_pre_sds,
                tcds.sds,
            )
            env_post_sds = environment_builder.build_post_sds()
            self._expectation_post_sds = self._expectation.post_sds(tcds.sds)

            self._check_post_sds(atc, env_post_sds)

    def _parse(self) -> ActionToCheck:
        atc = self._actor.parse(self._instructions)
        self._check_symbols_after(atc, phase_step.STEP__ACT__PARSE)

        return atc

    def _check_pre_sds(self, atc: ActionToCheck, env: InstructionEnvironmentForPreSdsStep):
        self._validate_pre_sds(atc, env)

    def _check_post_sds(self,
                        atc: ActionToCheck,
                        env: InstructionEnvironmentForPostSdsStep,
                        ):
        self._validate_post_sds(atc, env)
        self._prepare(atc, env)
        self._execute(atc, env)

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
            raise StopAssertion()

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
            raise StopAssertion()

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
            raise StopAssertion()

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
