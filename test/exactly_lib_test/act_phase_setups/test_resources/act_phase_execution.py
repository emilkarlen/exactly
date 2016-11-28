import os
import pathlib
import unittest

from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.act_phase_handling import ExitCodeOrHardError, ActSourceAndExecutorConstructor, \
    new_eh_exit_code, \
    ActSourceAndExecutor, ActPhaseOsProcessExecutor
from exactly_lib.test_case.os_services import ACT_PHASE_OS_PROCESS_EXECUTOR
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.failure_details import FailureDetails
from exactly_lib.util.std import StdFiles
from exactly_lib_test.execution.test_resources import eh_check
from exactly_lib_test.instructions.test_resources.assertion_utils import sh_check
from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources import file_structure_utils as fs_utils
from exactly_lib_test.test_resources.execution.utils import sandbox_directory_structure
from exactly_lib_test.test_resources.process import capture_process_executor_result, ProcessExecutor
from exactly_lib_test.test_resources.value_assertions import value_assertion as va
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder


class HardErrorResultError(Exception):
    def __init__(self,
                 result: ExitCodeOrHardError,
                 failure_details: FailureDetails):
        self.result = result
        self.failure_details = failure_details


class Arrangement:
    def __init__(self,
                 executor_constructor: ActSourceAndExecutorConstructor,
                 act_phase_instructions: list,
                 home_dir_contents: file_structure.DirContents = file_structure.DirContents([]),
                 environ: dict = None,
                 timeout_in_seconds: int = None,
                 act_phase_process_executor: ActPhaseOsProcessExecutor = ACT_PHASE_OS_PROCESS_EXECUTOR
                 ):
        self.executor_constructor = executor_constructor
        self.act_phase_instructions = act_phase_instructions
        self.home_dir_contents = home_dir_contents
        self.environ = {} if environ is None else environ
        self.timeout_in_seconds = timeout_in_seconds
        self.act_phase_process_executor = act_phase_process_executor


class Expectation:
    def __init__(self,
                 side_effects_on_files_after_execute: va.ValueAssertion = va.anything_goes(),
                 side_effects_on_files_after_prepare: va.ValueAssertion = va.anything_goes(),
                 result_of_prepare: va.ValueAssertion = sh_check.is_success(),
                 result_of_execute: va.ValueAssertion = eh_check.is_any_exit_code,
                 sub_process_result_from_execute: va.ValueAssertion = va.anything_goes()):
        self.side_effects_on_files_after_prepare = side_effects_on_files_after_prepare
        self.side_effects_on_files_after_execute = side_effects_on_files_after_execute
        self.result_of_prepare = result_of_prepare
        self.result_of_execute = result_of_execute
        self.sub_process_result_from_execute = sub_process_result_from_execute


def simple_success() -> Expectation:
    return Expectation()


def check_execution(put: unittest.TestCase,
                    arrangement: Arrangement,
                    expectation: Expectation) -> ExitCodeOrHardError:
    assert_is_list_of_act_phase_instructions(put, arrangement.act_phase_instructions)

    cwd_before_test = os.getcwd()
    with fs_utils.tmp_dir(arrangement.home_dir_contents) as home_dir:
        environment = InstructionEnvironmentForPreSdsStep(home_dir,
                                                          arrangement.environ,
                                                          arrangement.timeout_in_seconds)
        sut = arrangement.executor_constructor.apply(arrangement.act_phase_process_executor,
                                                     environment,
                                                     arrangement.act_phase_instructions)
        step_result = sut.validate_pre_sds(environment)
        put.assertEqual(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                        step_result.status,
                        'Result of validation/pre-sds')
        with sandbox_directory_structure() as sds:
            environment = InstructionEnvironmentForPostSdsStep(environment.home_directory,
                                                               environment.environ,
                                                               sds,
                                                               phase_identifier.ACT.identifier,
                                                               environment.timeout_in_seconds)
            try:
                os.chdir(str(sds.act_dir))
                step_result = sut.validate_post_setup(environment)
                put.assertEqual(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                step_result.status,
                                'Result of validation/post-setup')
                script_output_dir_path = sds.test_case_dir
                step_result = sut.prepare(environment, script_output_dir_path)
                expectation.side_effects_on_files_after_prepare.apply(put, sds)
                expectation.result_of_prepare.apply(put,
                                                    step_result,
                                                    MessageBuilder('Result of prepare'))
                if not step_result.is_success:
                    return

                process_executor = ProcessExecutorForProgramExecutorThatRaisesIfResultIsNotExitCode(
                    environment,
                    script_output_dir_path,
                    sut)
                error_msg_extra_info = ''
                sub_process_result = None
                try:
                    sub_process_result = capture_process_executor_result(process_executor,
                                                                         sds.result.root_dir)
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
                expectation.side_effects_on_files_after_execute.apply(put, sds)
                return step_result
            finally:
                os.chdir(cwd_before_test)


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
