import os

from exactly_lib.execution import partial_execution
from exactly_lib.execution.instruction_execution import phase_step_executors, phase_step_execution
from exactly_lib.execution.phase_step_identifiers import phase_step
from exactly_lib.section_document.model import SectionContents
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.os_services import ACT_PHASE_OS_PROCESS_EXECUTOR
from exactly_lib.test_case.phases import setup
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib.test_case.test_case_status import ExecutionMode
from exactly_lib.test_case_file_structure import environment_variables
from exactly_lib.util.symbol_table import SymbolTable
from . import result
from .result import FullResult, PartialResult, PartialResultStatus, FullResultStatus


class PredefinedProperties:
    """Properties that are forwarded to the right place in the execution."""

    def __init__(self,
                 predefined_symbols: SymbolTable = None):
        self.__predefined_symbols = predefined_symbols

    @property
    def predefined_symbols(self) -> SymbolTable:
        return self.__predefined_symbols


def execute(test_case: test_case_doc.TestCase,
            predefined_properties: PredefinedProperties,
            configuration_builder: ConfigurationBuilder,
            sandbox_directory_root_name_prefix: str,
            is_keep_sandbox: bool) -> FullResult:
    """
    The main method for executing a Test Case.
    """
    partial_result = _execute_configuration_phase(configuration_builder,
                                                  test_case.configuration_phase)
    if partial_result.status is not PartialResultStatus.PASS:
        return new_configuration_phase_failure_from(partial_result)
    if configuration_builder.execution_mode is ExecutionMode.SKIP:
        return result.new_skipped()
    environ = dict(os.environ)
    _prepare_environment_variables(environ)
    partial_execution_configuration = partial_execution.Configuration(
        ACT_PHASE_OS_PROCESS_EXECUTOR,
        configuration_builder.hds,
        environ,
        configuration_builder.timeout_in_seconds,
        predefined_symbols=predefined_properties.predefined_symbols,
    )
    partial_result = partial_execution.execute(configuration_builder.act_phase_handling,
                                               partial_execution.TestCase(test_case.setup_phase,
                                                                          test_case.act_phase,
                                                                          test_case.before_assert_phase,
                                                                          test_case.assert_phase,
                                                                          test_case.cleanup_phase),
                                               partial_execution_configuration,
                                               setup.default_settings(),
                                               sandbox_directory_root_name_prefix,
                                               is_keep_sandbox)
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
                      partial_result.sds,
                      partial_result.failure_info)


def translate_status(execution_mode: ExecutionMode,
                     ps: PartialResultStatus) -> FullResultStatus:
    """
    :param execution_mode: Must not be ExecutionMode.SKIPPED
    """
    if execution_mode is ExecutionMode.FAIL:
        if ps is PartialResultStatus.FAIL:
            return FullResultStatus.XFAIL
        elif ps is PartialResultStatus.PASS:
            return FullResultStatus.XPASS
    return FullResultStatus(ps.value)


def _prepare_environment_variables(environ: dict):
    for ev in environment_variables.ALL_ENV_VARS:
        if ev in environ:
            del environ[ev]


def _execute_configuration_phase(phase_environment: ConfigurationBuilder,
                                 configuration_phase: SectionContents) -> PartialResult:
    return phase_step_execution.execute_phase(configuration_phase,
                                              phase_step_execution.ElementHeaderExecutorThatDoesNothing(),
                                              phase_step_execution.ElementHeaderExecutorThatDoesNothing(),
                                              phase_step_executors.ConfigurationMainExecutor(phase_environment),
                                              phase_step.CONFIGURATION__MAIN,
                                              None)
