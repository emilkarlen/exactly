import os
import unittest
from contextlib import contextmanager
from typing import List, Optional, Sequence, ContextManager

from exactly_lib.execution import phase_step
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case.actor import Actor, ActionToCheck, AtcOsProcessExecutor
from exactly_lib.test_case.atc_os_proc_executors import DEFAULT_ATC_OS_PROCESS_EXECUTOR
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result import svh, sh
from exactly_lib.test_case.result.eh import ExitCodeOrHardError, new_eh_exit_code
from exactly_lib.test_case.result.failure_details import FailureDetails
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.file_utils.std import StdFiles
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.execution.test_resources import eh_assertions
from exactly_lib_test.test_case.result.test_resources import sh_assertions, svh_assertions
from exactly_lib_test.test_case.test_resources.arrangements import ProcessExecutionArrangement
from exactly_lib_test.test_case.test_resources.instruction_environment import InstructionEnvironmentPostSdsBuilder
from exactly_lib_test.test_case_file_structure.test_resources import hds_populators
from exactly_lib_test.test_case_file_structure.test_resources.hds_utils import home_directory_structure
from exactly_lib_test.test_resources.process import capture_process_executor_result, SubProcessResult, ProcessExecutor
from exactly_lib_test.test_resources.tcds_and_symbols.sds_env_utils import sds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder, ValueAssertion


class HardErrorResultError(Exception):
    def __init__(self,
                 result: ExitCodeOrHardError,
                 failure_details: FailureDetails):
        self.result = result
        self.failure_details = failure_details


class Arrangement:
    def __init__(self,
                 hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
                 atc_process_executor: AtcOsProcessExecutor = DEFAULT_ATC_OS_PROCESS_EXECUTOR,
                 symbol_table: Optional[SymbolTable] = None,
                 process_execution: ProcessExecutionArrangement = ProcessExecutionArrangement(
                     process_execution_settings=ProcessExecutionSettings.with_no_timeout_no_environ()
                 ),
                 stdin_contents: str = '',
                 ):
        self.symbol_table = symbol_table_from_none_or_value(symbol_table)
        self.hds_contents = hds_contents
        self.atc_process_executor = atc_process_executor
        self.process_execution = process_execution
        self.stdin_contents = stdin_contents

    @property
    def proc_exe_settings(self) -> ProcessExecutionSettings:
        return self.process_execution.process_execution_settings


class Expectation:
    def __init__(self,
                 validate_pre_sds: ValueAssertion[svh.SuccessOrValidationErrorOrHardError]
                 = svh_assertions.is_success(),
                 prepare: ValueAssertion[sh.SuccessOrHardError]
                 = sh_assertions.is_success(),
                 execute: ValueAssertion[ExitCodeOrHardError]
                 = eh_assertions.is_any_exit_code,
                 symbol_usages: ValueAssertion[Sequence[SymbolUsage]] =
                 asrt.is_empty_sequence,
                 side_effects_on_files_after_execute: ValueAssertion[SandboxDirectoryStructure]
                 = asrt.anything_goes(),
                 side_effects_on_files_after_prepare: ValueAssertion[SandboxDirectoryStructure] =
                 asrt.anything_goes(),
                 sub_process_result_from_execute: ValueAssertion[SubProcessResult] = asrt.anything_goes()):
        self.symbol_usages = symbol_usages
        self.validate_pre_sds = validate_pre_sds
        self.prepare = prepare
        self.execute = execute
        self.side_effects_on_files_after_prepare = side_effects_on_files_after_prepare
        self.side_effects_on_files_after_execute = side_effects_on_files_after_execute
        self.sub_process_result_from_execute = sub_process_result_from_execute


def simple_success() -> Expectation:
    return Expectation()


def check_execution(put: unittest.TestCase,
                    actor: Actor,
                    act_phase_instructions: List[ActPhaseInstruction],
                    arrangement: Arrangement,
                    expectation: Expectation,
                    ) -> ExitCodeOrHardError:
    checker = _Checker(put, actor, act_phase_instructions, arrangement, expectation)
    return checker.check()


class ProcessExecutorForProgramExecutorThatRaisesIfResultIsNotExitCode(ProcessExecutor):
    """
    An executor that raises HardErrorResultError if result is not an exit code.
    """

    def __init__(self,
                 environment: InstructionEnvironmentForPostSdsStep,
                 atc_process_executor: AtcOsProcessExecutor,
                 atc: ActionToCheck):
        self.environment = environment
        self.atc_process_executor = atc_process_executor
        self.atc = atc

    def execute(self, files: StdFiles) -> int:
        """
         :raises HardErrorResultError: Return value from executor is not an exit code.
        """
        exit_code_or_hard_error = self.atc.execute(self.environment,
                                                   self.atc_process_executor,
                                                   files)
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

    def check(self) -> Optional[ExitCodeOrHardError]:
        try:
            self._check()
        except _CheckIsDoneException:
            return None

    def _check(self) -> Optional[ExitCodeOrHardError]:
        atc = self._parse()
        with self._pre_sds_env() as env_pre_sds:
            self._validate_pre_sds(atc, env_pre_sds)

            with self._post_sds_env(env_pre_sds) as env_post_sds:
                self._validate_post_sds(atc, env_post_sds)
                self._prepare(atc, env_post_sds)
                return self._execute(atc, env_post_sds)

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
                symbols=self._arrangement.symbol_table)
            yield instruction_environment

    @staticmethod
    @contextmanager
    def _post_sds_env(env_pre_sds: InstructionEnvironmentForPreSdsStep,
                      ) -> ContextManager[InstructionEnvironmentForPostSdsStep]:
        with sds_with_act_as_curr_dir(symbols=env_pre_sds.symbols
                                      ) as path_resolving_env:
            environment_builder = InstructionEnvironmentPostSdsBuilder.new_from_pre_sds(
                env_pre_sds,
                path_resolving_env.sds,
            )
            yield environment_builder.build_post_sds()

    def _validate_pre_sds(self,
                          atc: ActionToCheck,
                          env: InstructionEnvironmentForPreSdsStep,
                          ):
        step_result = atc.validate_pre_sds(env)
        self._expectation.validate_pre_sds.apply_with_message(
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
        self._put.assertEqual(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                              step_result.status,
                              'Result of validation/post-setup')
        self._check_symbols_after(atc, phase_step.STEP__VALIDATE_POST_SETUP)

    def _prepare(self,
                 atc: ActionToCheck,
                 env: InstructionEnvironmentForPostSdsStep,
                 ):
        step_result = atc.prepare(env, self._arrangement.atc_process_executor)
        self._expectation.side_effects_on_files_after_prepare.apply(self._put, env.sds)
        self._expectation.prepare.apply(self._put,
                                        step_result,
                                        MessageBuilder('Result of prepare'))
        self._check_symbols_after(atc, phase_step.STEP__ACT__PREPARE)
        if not step_result.is_success:
            raise _CheckIsDoneException()

    def _execute(self,
                 atc: ActionToCheck,
                 env: InstructionEnvironmentForPostSdsStep,
                 ) -> Optional[ExitCodeOrHardError]:
        process_executor = ProcessExecutorForProgramExecutorThatRaisesIfResultIsNotExitCode(
            env,
            self._arrangement.atc_process_executor,
            atc)
        error_msg_extra_info = ''
        sub_process_result = None
        try:
            sub_process_result = capture_process_executor_result(process_executor,
                                                                 env.sds.result.root_dir,
                                                                 self._arrangement.stdin_contents)
            step_result = new_eh_exit_code(sub_process_result.exitcode)
        except HardErrorResultError as ex:
            step_result = ex.result
            error_msg_extra_info = os.linesep + str(ex.failure_details) + os.linesep

        self._expectation.execute.apply(self._put,
                                        step_result,
                                        MessageBuilder('Result of execute' + error_msg_extra_info))
        if sub_process_result:
            msg_builder = MessageBuilder('Sub process output from execute ' + error_msg_extra_info)
            self._expectation.sub_process_result_from_execute.apply(self._put, sub_process_result, msg_builder)
        self._expectation.side_effects_on_files_after_execute.apply(self._put, env.sds)

        self._check_symbols_after(atc, phase_step.STEP__ACT__EXECUTE)

        return step_result

    def _check_symbols_after(self, atc: ActionToCheck, step: str):
        self._expectation.symbol_usages.apply_with_message(
            self._put,
            atc.symbol_usages(),
            'symbol-usages after ' + step)


class _CheckIsDoneException(Exception):
    pass
