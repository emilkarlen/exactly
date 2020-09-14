from exactly_lib.execution import phase_step
from exactly_lib.execution.failure_info import ActPhaseFailureInfo
from exactly_lib.execution.full_execution.result import FullExeResultStatus, FullExeResult
from exactly_lib.test_case.result.failure_details import FailureDetails
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure

DUMMY_SDS = SandboxDirectoryStructure('test-root-dir')


def full_result_with_failure_info(status: FullExeResultStatus,
                                  failure_phase_step=phase_step.ASSERT__MAIN) -> FullExeResult:
    return FullExeResult(status,
                         DUMMY_SDS,
                         None,
                         ActPhaseFailureInfo(failure_phase_step,
                                             FailureDetails.new_constant_message(
                                                 'failure message'),
                                             'actor name',
                                             'phase source'))


def full_result_without_failure_info(status: FullExeResultStatus) -> FullExeResult:
    return FullExeResult(status,
                         DUMMY_SDS,
                         None,
                         None)


FULL_RESULT_XFAIL = full_result_with_failure_info(FullExeResultStatus.XFAIL)
FULL_RESULT_XPASS = full_result_without_failure_info(FullExeResultStatus.XPASS)
FULL_RESULT_HARD_ERROR = full_result_with_failure_info(FullExeResultStatus.HARD_ERROR)
FULL_RESULT_VALIDATE = full_result_with_failure_info(FullExeResultStatus.VALIDATION_ERROR)
FULL_RESULT_INTERNAL_ERROR = full_result_with_failure_info(FullExeResultStatus.INTERNAL_ERROR)
