from typing import Optional

from exactly_lib.execution import phase_step
from exactly_lib.execution.configuration import ExecutionConfiguration
from exactly_lib.execution.full_execution.result import FullExeResult, FullExeResultStatus, \
    new_from_result_of_partial_execution
from exactly_lib.execution.full_execution.result import new_skipped
from exactly_lib.execution.impl import phase_step_executors, phase_step_execution
from exactly_lib.execution.partial_execution import execution
from exactly_lib.execution.partial_execution.configuration import ConfPhaseValues, TestCase
from exactly_lib.execution.result import ExecutionFailureStatus, PhaseStepFailure
from exactly_lib.section_document.model import SectionContents
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.phases import setup
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib.test_case.test_case_status import TestCaseStatus


def execute(conf: ExecutionConfiguration,
            configuration_builder: ConfigurationBuilder,
            is_keep_sandbox: bool,
            test_case: test_case_doc.TestCase,
            ) -> FullExeResult:
    """
    The main method for executing a Test Case.
    """
    conf_phase_failure = execute_configuration_phase(configuration_builder,
                                                     test_case.configuration_phase)
    if conf_phase_failure is not None:
        return new_configuration_phase_failure_from(conf_phase_failure)
    if configuration_builder.test_case_status is TestCaseStatus.SKIP:
        return new_skipped()
    conf_phase_values = ConfPhaseValues(
        configuration_builder.actor,
        configuration_builder.hds,
        configuration_builder.timeout_in_seconds,
    )
    partial_result = execution.execute(
        TestCase(test_case.setup_phase,
                 test_case.act_phase,
                 test_case.before_assert_phase,
                 test_case.assert_phase,
                 test_case.cleanup_phase),
        conf,
        conf_phase_values,
        setup.default_settings(),
        is_keep_sandbox)
    return new_from_result_of_partial_execution(configuration_builder.test_case_status,
                                                partial_result)


def execute_configuration_phase(phase_environment: ConfigurationBuilder,
                                configuration_phase: SectionContents) -> Optional[PhaseStepFailure]:
    return phase_step_execution.execute_phase(configuration_phase,
                                              phase_step_execution.ElementHeaderExecutorThatDoesNothing(),
                                              phase_step_execution.ElementHeaderExecutorThatDoesNothing(),
                                              phase_step_executors.ConfigurationMainExecutor(phase_environment),
                                              phase_step.CONFIGURATION__MAIN)


def new_configuration_phase_failure_from(phase_result: PhaseStepFailure) -> FullExeResult:
    full_status = FullExeResultStatus.HARD_ERROR
    if phase_result.status is ExecutionFailureStatus.IMPLEMENTATION_ERROR:
        full_status = FullExeResultStatus.IMPLEMENTATION_ERROR
    return FullExeResult(full_status,
                         None,
                         None,
                         phase_result.failure_info)
