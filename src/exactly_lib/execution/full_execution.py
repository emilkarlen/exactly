import os

from exactly_lib.execution import environment_variables
from exactly_lib.execution import partial_execution
from exactly_lib.execution.instruction_execution import phase_step_executors, phase_step_execution
from exactly_lib.execution.phase_step_identifiers import phase_step
from exactly_lib.section_document.model import SectionContents
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.execution_mode import ExecutionMode
from exactly_lib.test_case.phases import setup
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from . import result
from .result import FullResult, PartialResult, PartialResultStatus, FullResultStatus


def execute(test_case: test_case_doc.TestCase,
            configuration_builder: ConfigurationBuilder,
            execution_directory_root_name_prefix: str,
            is_keep_execution_directory_root: bool) -> FullResult:
    """
    The main method for executing a Test Case.
    """
    _prepare_environment_variables()
    partial_result = _execute_configuration_phase(configuration_builder,
                                                  test_case.configuration_phase)
    if partial_result.status is not PartialResultStatus.PASS:
        return new_configuration_phase_failure_from(partial_result)
    if configuration_builder.execution_mode is ExecutionMode.SKIP:
        return result.new_skipped()
    partial_execution_configuration = partial_execution.Configuration(configuration_builder.home_dir_path,
                                                                      configuration_builder.timeout_in_seconds)
    partial_result = partial_execution.execute(configuration_builder.act_phase_handling,
                                               partial_execution.TestCase(test_case.setup_phase,
                                                                          test_case.act_phase,
                                                                          test_case.before_assert_phase,
                                                                          test_case.assert_phase,
                                                                          test_case.cleanup_phase),
                                               partial_execution_configuration,
                                               setup.default_settings(),
                                               execution_directory_root_name_prefix,
                                               is_keep_execution_directory_root)
    return new_named_phases_result_from(configuration_builder.execution_mode,
                                        partial_result)


def new_configuration_phase_failure_from(partial_result: PartialResult) -> FullResult:
    full_status = FullResultStatus.HARD_ERROR
    if partial_result.status is PartialResultStatus.IMPLEMENTATION_ERROR:
        full_status = FullResultStatus.IMPLEMENTATION_ERROR
    return FullResult(full_status,
                      None,
                      partial_result.failure_info)


def new_named_phases_result_from(execution_mode: ExecutionMode,
                                 partial_result: PartialResult) -> FullResult:
    return FullResult(translate_status(execution_mode, partial_result.status),
                      partial_result.sandbox_directory_structure,
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


def _execute_configuration_phase(phase_environment: ConfigurationBuilder,
                                 configuration_phase: SectionContents) -> PartialResult:
    return phase_step_execution.execute_phase(configuration_phase,
                                              phase_step_execution.ElementHeaderExecutorThatDoesNothing(),
                                              phase_step_execution.ElementHeaderExecutorThatDoesNothing(),
                                              phase_step_executors.ConfigurationMainExecutor(phase_environment),
                                              phase_step.CONFIGURATION__MAIN,
                                              None)
