from shelltest.execution.partial_execution import execute_partial

__author__ = 'emil'

import pathlib

from shelltest.execution import phase_step_executors
from shelltest import phases
from shelltest.exec_abs_syn import script_stmt_gen, abs_syn_gen
from shelltest.exec_abs_syn.instructions import PhaseEnvironmentForAnonymousPhase, ExecutionMode
from .result import FullResult, PartialResult, PartialResultStatus, FullResultStatus
from . import result
from . import phase_step_executor


def new_anonymous_phase_failure_from(partial_result: PartialResult) -> FullResult:
    full_status = FullResultStatus.HARD_ERROR
    if partial_result.status is PartialResultStatus.IMPLEMENTATION_ERROR:
        full_status = FullResultStatus.IMPLEMENTATION_ERROR
    return FullResult(full_status,
                      None,
                      partial_result.instruction_failure_info)


def new_named_phases_result_from(anonymous_phase_environment: PhaseEnvironmentForAnonymousPhase,
                                 partial_result: PartialResult) -> FullResult:
    def translate_status(ps: PartialResultStatus) -> FullResultStatus:
        if anonymous_phase_environment.execution_mode is ExecutionMode.NORMAL:
            return FullResultStatus(ps.value)
        raise NotImplementedError('not impl statuts translation')

    return FullResult(translate_status(partial_result.status),
                      partial_result.execution_directory_structure,
                      partial_result.instruction_failure_info)


def execute(script_file_manager: script_stmt_gen.ScriptFileManager,
            script_source_writer: script_stmt_gen.ScriptSourceBuilder,
            test_case: abs_syn_gen.TestCase,
            initial_home_dir_path: pathlib.Path,
            execution_directory_root_name_prefix: str,
            is_keep_execution_directory_root: bool) -> FullResult:
    anonymous_phase_environment = PhaseEnvironmentForAnonymousPhase(str(initial_home_dir_path))
    partial_result = execute_anonymous_phase(anonymous_phase_environment,
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
    return new_named_phases_result_from(anonymous_phase_environment,
                                        partial_result)


def execute_anonymous_phase(phase_environment: PhaseEnvironmentForAnonymousPhase,
                            test_case: abs_syn_gen.TestCase) -> PartialResult:
    return phase_step_executor.execute_phase(test_case.anonymous_phase,
                                             phase_step_executor.ElementHeaderExecutorThatDoesNothing(),
                                             phase_step_executor.ElementHeaderExecutorThatDoesNothing(),
                                             phase_step_executors.AnonymousPhaseInstructionExecutor(phase_environment),
                                             phases.ANONYMOUS,
                                             None,
                                             None)


