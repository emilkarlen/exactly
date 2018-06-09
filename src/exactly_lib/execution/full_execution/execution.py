import os
from typing import Dict

from exactly_lib.execution import phase_step
from exactly_lib.execution.full_execution.configuration import PredefinedProperties
from exactly_lib.execution.full_execution.result import FullResult, new_configuration_phase_failure_from, \
    new_named_phases_result_from
from exactly_lib.execution.full_execution.result import new_skipped
from exactly_lib.execution.impl import phase_step_executors, phase_step_execution
from exactly_lib.execution.partial_execution import execution
from exactly_lib.execution.partial_execution.configuration import Configuration, TestCase
from exactly_lib.execution.partial_execution.result import PartialResultStatus, PartialResult
from exactly_lib.execution.sandbox_dir_resolving import SandboxRootDirNameResolver
from exactly_lib.section_document.model import SectionContents
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.act_phase_handling import ActPhaseOsProcessExecutor
from exactly_lib.test_case.phases import setup
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib.test_case.test_case_status import ExecutionMode
from exactly_lib.test_case_file_structure import environment_variables


def execute(test_case: test_case_doc.TestCase,
            predefined_properties: PredefinedProperties,
            configuration_builder: ConfigurationBuilder,
            act_phase_sub_process_executor: ActPhaseOsProcessExecutor,
            sandbox_root_dir_resolver: SandboxRootDirNameResolver,
            is_keep_sandbox: bool) -> FullResult:
    """
    The main method for executing a Test Case.
    """
    partial_result = _execute_configuration_phase(configuration_builder,
                                                  test_case.configuration_phase)
    if partial_result.status is not PartialResultStatus.PASS:
        return new_configuration_phase_failure_from(partial_result)
    if configuration_builder.execution_mode is ExecutionMode.SKIP:
        return new_skipped()
    environ = dict(os.environ)
    _prepare_environment_variables(environ)
    partial_execution_configuration = Configuration(
        act_phase_sub_process_executor,
        configuration_builder.hds,
        environ,
        configuration_builder.timeout_in_seconds,
        predefined_symbols=predefined_properties.predefined_symbols,
    )
    partial_result = execution.execute(
        configuration_builder.act_phase_handling,
        TestCase(test_case.setup_phase,
                 test_case.act_phase,
                 test_case.before_assert_phase,
                 test_case.assert_phase,
                 test_case.cleanup_phase),
        partial_execution_configuration,
        setup.default_settings(),
        sandbox_root_dir_resolver,
        is_keep_sandbox)
    return new_named_phases_result_from(configuration_builder.execution_mode,
                                        partial_result)


def _prepare_environment_variables(environ: Dict[str, str]):
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
