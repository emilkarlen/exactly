import os
import pathlib

from shellcheck_lib.document.model import PhaseContents
from shellcheck_lib.execution import environment_variables
from shellcheck_lib.execution import phase_step_executors, partial_execution, phase_step
from shellcheck_lib.execution.partial_execution import ScriptHandling
from shellcheck_lib.test_case import test_case_doc
from shellcheck_lib.test_case.sections.anonymous import ConfigurationBuilder, ExecutionMode
from . import phase_step_execution
from . import result
from .result import FullResult, PartialResult, PartialResultStatus, FullResultStatus


def execute(script_handling: ScriptHandling,
            test_case: test_case_doc.TestCase,
            initial_home_dir_path: pathlib.Path,
            execution_directory_root_name_prefix: str,
            is_keep_execution_directory_root: bool) -> FullResult:
    """
    The main method for executing a Test Case.
    """
    _prepare_environment_variables()
    anonymous_phase_environment = ConfigurationBuilder(initial_home_dir_path)
    partial_result = _execute_anonymous_phase(anonymous_phase_environment,
                                              test_case.anonymous_phase)
    if partial_result.status is not PartialResultStatus.PASS:
        return new_anonymous_phase_failure_from(partial_result)
    if anonymous_phase_environment.execution_mode is ExecutionMode.SKIPPED:
        return result.new_skipped()
    partial_result = partial_execution.execute(script_handling,
                                               partial_execution.TestCase(test_case.setup_phase,
                                                                          test_case.act_phase,
                                                                          test_case.assert_phase,
                                                                          test_case.cleanup_phase),
                                               anonymous_phase_environment.home_dir_path,
                                               execution_directory_root_name_prefix,
                                               is_keep_execution_directory_root)
    return new_named_phases_result_from(anonymous_phase_environment.execution_mode,
                                        partial_result)


def new_anonymous_phase_failure_from(partial_result: PartialResult) -> FullResult:
    full_status = FullResultStatus.HARD_ERROR
    if partial_result.status is PartialResultStatus.IMPLEMENTATION_ERROR:
        full_status = FullResultStatus.IMPLEMENTATION_ERROR
    return FullResult(full_status,
                      None,
                      partial_result.failure_info)


def new_named_phases_result_from(execution_mode: ExecutionMode,
                                 partial_result: PartialResult) -> FullResult:
    return FullResult(translate_status(execution_mode, partial_result.status),
                      partial_result.execution_directory_structure,
                      partial_result.failure_info)


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


def _prepare_environment_variables():
    for ev in environment_variables.ALL_ENV_VARS:
        if ev in os.environ:
            del os.environ[ev]


def _execute_anonymous_phase(phase_environment: ConfigurationBuilder,
                             anonymous_phase: PhaseContents) -> PartialResult:
    return phase_step_execution.execute_phase(anonymous_phase,
                                              phase_step_execution.ElementHeaderExecutorThatDoesNothing(),
                                              phase_step_execution.ElementHeaderExecutorThatDoesNothing(),
                                              phase_step_executors.AnonymousInstructionExecutor(phase_environment),
                                              phase_step.ANONYMOUS_MAIN,
                                              None)
