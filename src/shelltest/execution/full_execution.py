import copy
import os
import pathlib

from shelltest.execution.partial_execution import execute_partial

from shelltest.execution import phase_step_executors
from shelltest import phases
from shelltest.exec_abs_syn import instructions
from shelltest.exec_abs_syn import script_stmt_gen, abs_syn_gen
from shelltest.exec_abs_syn.instructions import PhaseEnvironmentForAnonymousPhase, ExecutionMode
from .result import FullResult, PartialResult, PartialResultStatus, FullResultStatus
from . import result
from . import phase_step_execution


def new_anonymous_phase_failure_from(partial_result: PartialResult) -> FullResult:
    full_status = FullResultStatus.HARD_ERROR
    if partial_result.status is PartialResultStatus.IMPLEMENTATION_ERROR:
        full_status = FullResultStatus.IMPLEMENTATION_ERROR
    return FullResult(full_status,
                      None,
                      partial_result.instruction_failure_info)


def new_named_phases_result_from(execution_mode: ExecutionMode,
                                 partial_result: PartialResult) -> FullResult:
    return FullResult(translate_status(execution_mode, partial_result.status),
                      partial_result.execution_directory_structure,
                      partial_result.instruction_failure_info)


def translate_status(execution_mode: ExecutionMode,
                     ps: PartialResultStatus) -> FullResultStatus:
    """
    :param execution_mode: Must not be ExecutionMode.SKIPPED
    """
    if execution_mode is ExecutionMode.XFAIL:
        if ps is PartialResultStatus.FAIL:
            return FullResultStatus.XFAIL
        elif ps is PartialResultStatus.PASS:
            return FullResultStatus.XPASS
    return FullResultStatus(ps.value)


def execute(script_file_manager: script_stmt_gen.ScriptFileManager,
            script_source_writer: script_stmt_gen.ScriptSourceBuilder,
            test_case: abs_syn_gen.TestCase,
            initial_home_dir_path: pathlib.Path,
            execution_directory_root_name_prefix: str,
            is_keep_execution_directory_root: bool) -> FullResult:
    saved_environment_variables = _prepare_and_save_environment_variables()
    anonymous_phase_environment = PhaseEnvironmentForAnonymousPhase(str(initial_home_dir_path))
    partial_result = _execute_anonymous_phase(anonymous_phase_environment,
                                              test_case)
    if partial_result.status is not PartialResultStatus.PASS:
        return new_anonymous_phase_failure_from(partial_result)
    if anonymous_phase_environment.execution_mode is ExecutionMode.SKIPPED:
        return result.new_skipped()
    partial_result = execute_partial(script_file_manager,
                                     script_source_writer,
                                     test_case,
                                     anonymous_phase_environment.home_dir_path,
                                     execution_directory_root_name_prefix,
                                     is_keep_execution_directory_root)
    os.environ = saved_environment_variables
    return new_named_phases_result_from(anonymous_phase_environment.execution_mode,
                                        partial_result)


def _prepare_and_save_environment_variables() -> dict:
    before = copy.deepcopy(os.environ)
    for ev in instructions.ALL_ENV_VARS:
        if ev in os.environ:
            del os.environ[ev]
    return before


def _execute_anonymous_phase(phase_environment: PhaseEnvironmentForAnonymousPhase,
                             test_case: abs_syn_gen.TestCase) -> PartialResult:
    return phase_step_execution.execute_phase(test_case.anonymous_phase,
                                              phase_step_execution.ElementHeaderExecutorThatDoesNothing(),
                                              phase_step_execution.ElementHeaderExecutorThatDoesNothing(),
                                              phase_step_executors.AnonymousPhaseInstructionExecutor(phase_environment),
                                              phases.ANONYMOUS,
                                              None,
                                              None)


