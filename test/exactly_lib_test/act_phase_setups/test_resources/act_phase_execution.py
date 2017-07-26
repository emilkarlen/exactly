import os
import pathlib
import unittest

from exactly_lib.execution.phase_step_identifiers import phase_step
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.act_phase_handling import ActSourceAndExecutorConstructor, \
    ActSourceAndExecutor, ActPhaseOsProcessExecutor
from exactly_lib.test_case.eh import ExitCodeOrHardError, new_eh_exit_code
from exactly_lib.test_case.os_services import ACT_PHASE_OS_PROCESS_EXECUTOR
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.failure_details import FailureDetails
from exactly_lib.util.std import StdFiles
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.execution.test_resources import eh_assertions
from exactly_lib_test.test_case_utils.test_resources import svh_assertions, sh_assertions
from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources.execution import tmp_dir as fs_utils
from exactly_lib_test.test_resources.process import capture_process_executor_result, ProcessExecutor
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.sds_env_utils import sds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder
from exactly_lib_test.util.test_resources.symbol_tables import symbol_table_from_none_or_value


class HardErrorResultError(Exception):
    def __init__(self,
                 result: ExitCodeOrHardError,
                 failure_details: FailureDetails):
        self.result = result
        self.failure_details = failure_details


class Arrangement:
    def __init__(self,
                 home_dir_contents: file_structure.DirContents = file_structure.DirContents([]),
                 environ: dict = None,
                 timeout_in_seconds: int = None,
                 act_phase_process_executor: ActPhaseOsProcessExecutor = ACT_PHASE_OS_PROCESS_EXECUTOR,
                 symbol_table: SymbolTable = None,
                 ):
        self.home_dir_contents = home_dir_contents
        self.environ = {} if environ is None else environ
        self.timeout_in_seconds = timeout_in_seconds
        self.act_phase_process_executor = act_phase_process_executor
        self.symbol_table = symbol_table_from_none_or_value(symbol_table)


class Expectation:
    def __init__(self,
                 result_of_validate_pre_sds: asrt.ValueAssertion = svh_assertions.is_success(),
                 result_of_prepare: asrt.ValueAssertion = sh_assertions.is_success(),
                 result_of_execute: asrt.ValueAssertion = eh_assertions.is_any_exit_code,
                 symbol_usages: asrt.ValueAssertion = asrt.is_empty_list,
                 side_effects_on_files_after_execute: asrt.ValueAssertion = asrt.anything_goes(),
                 side_effects_on_files_after_prepare: asrt.ValueAssertion = asrt.anything_goes(),
                 sub_process_result_from_execute: asrt.ValueAssertion = asrt.anything_goes()):
        self.result_of_validate_pre_sds = result_of_validate_pre_sds
        self.symbol_usages = symbol_usages
        self.side_effects_on_files_after_prepare = side_effects_on_files_after_prepare
        self.side_effects_on_files_after_execute = side_effects_on_files_after_execute
        self.result_of_prepare = result_of_prepare
        self.result_of_execute = result_of_execute
        self.sub_process_result_from_execute = sub_process_result_from_execute


def simple_success() -> Expectation:
    return Expectation()


def check_execution(put: unittest.TestCase,
                    executor_constructor: ActSourceAndExecutorConstructor,
                    act_phase_instructions: list,
                    arrangement: Arrangement,
                    expectation: Expectation) -> ExitCodeOrHardError:
    assert_is_list_of_act_phase_instructions(put, act_phase_instructions)
    with fs_utils.tmp_dir(arrangement.home_dir_contents) as home_dir:
        instruction_environment = InstructionEnvironmentForPreSdsStep(home_dir,
                                                                      arrangement.environ,
                                                                      arrangement.timeout_in_seconds,
                                                                      symbols=arrangement.symbol_table)
        sut = executor_constructor.apply(arrangement.act_phase_process_executor,
                                         instruction_environment,
                                         act_phase_instructions)
        sut.parse(instruction_environment)
        expectation.symbol_usages.apply_with_message(put,
                                                     sut.symbol_usages(),
                                                     'symbol-usages after ' +
                                                     phase_step.STEP__ACT__PARSE)
        step_result = sut.validate_pre_sds(instruction_environment)
        expectation.result_of_validate_pre_sds.apply_with_message(put, step_result,
                                                                  'validate_pre_sds')
        if step_result.status is not svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS:
            return None
        put.assertEqual(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                        step_result.status,
                        'Result of ' + phase_step.STEP__VALIDATE_PRE_SDS)
        expectation.symbol_usages.apply_with_message(put,
                                                     sut.symbol_usages(),
                                                     'symbol-usages after ' +
                                                     phase_step.STEP__VALIDATE_PRE_SDS)
        with sds_with_act_as_curr_dir(symbols=instruction_environment.symbols
                                      ) as path_resolving_env:
            instruction_environment = InstructionEnvironmentForPostSdsStep(instruction_environment.home_directory,
                                                                           instruction_environment.environ,
                                                                           path_resolving_env.sds,
                                                                           phase_identifier.ACT.identifier,
                                                                           instruction_environment.timeout_in_seconds,
                                                                           symbols=arrangement.symbol_table)
            step_result = sut.validate_post_setup(instruction_environment)
            put.assertEqual(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                            step_result.status,
                            'Result of validation/post-setup')
            expectation.symbol_usages.apply_with_message(put,
                                                         sut.symbol_usages(),
                                                         'symbol-usages after ' +
                                                         phase_step.STEP__VALIDATE_POST_SETUP)
            script_output_dir_path = path_resolving_env.sds.test_case_dir
            step_result = sut.prepare(instruction_environment, script_output_dir_path)
            expectation.side_effects_on_files_after_prepare.apply(put, path_resolving_env.sds)
            expectation.result_of_prepare.apply(put,
                                                step_result,
                                                MessageBuilder('Result of prepare'))
            expectation.symbol_usages.apply_with_message(put,
                                                         sut.symbol_usages(),
                                                         'symbol-usages after ' +
                                                         phase_step.STEP__ACT__PREPARE)
            if not step_result.is_success:
                return

            process_executor = ProcessExecutorForProgramExecutorThatRaisesIfResultIsNotExitCode(
                instruction_environment,
                script_output_dir_path,
                sut)
            error_msg_extra_info = ''
            sub_process_result = None
            try:
                sub_process_result = capture_process_executor_result(process_executor,
                                                                     path_resolving_env.sds.result.root_dir)
                step_result = new_eh_exit_code(sub_process_result.exitcode)
            except HardErrorResultError as ex:
                step_result = ex.result
                error_msg_extra_info = os.linesep + str(ex.failure_details) + os.linesep

            expectation.result_of_execute.apply(put,
                                                step_result,
                                                MessageBuilder('Result of execute' + error_msg_extra_info))
            if sub_process_result:
                msg_builder = MessageBuilder('Sub process output from execute' + error_msg_extra_info)
                expectation.sub_process_result_from_execute.apply(put, sub_process_result, msg_builder)
            expectation.side_effects_on_files_after_execute.apply(put, path_resolving_env.sds)
            expectation.symbol_usages.apply_with_message(put,
                                                         sut.symbol_usages(),
                                                         'symbol-usages after ' +
                                                         phase_step.STEP__ACT__EXECUTE)
            return step_result


def assert_is_list_of_act_phase_instructions(put: unittest.TestCase, x):
    put.assertIsInstance(x, list,
                         'Invalid test input: Expecting list of ActPhaseInstruction:s. Found: ' + str(type(x)))
    i = 0
    for e in x:
        put.assertIsInstance(e, ActPhaseInstruction,
                             'Invalid test input: Element [%d]. Expecting an ActPhaseInstruction:s. Found: %s' %
                             (i, type(e)))
        i += 1


class ProcessExecutorForProgramExecutorThatRaisesIfResultIsNotExitCode(ProcessExecutor):
    """
    An executor that raises HardErrorResultError if result is not an exit code.
    """

    def __init__(self,
                 environment: InstructionEnvironmentForPostSdsStep,
                 script_output_path: pathlib.Path,
                 program_executor: ActSourceAndExecutor):
        self.program_executor = program_executor
        self.environment = environment
        self.script_output_path = script_output_path

    def execute(self,
                files: StdFiles) -> int:
        """
         :raises HardErrorResultError: Return value from executor is not an exit code.
        """
        exit_code_or_hard_error = self.program_executor.execute(self.environment,
                                                                self.script_output_path,
                                                                files)
        if exit_code_or_hard_error.is_exit_code:
            return exit_code_or_hard_error.exit_code
        raise HardErrorResultError(exit_code_or_hard_error,
                                   exit_code_or_hard_error.failure_details)
