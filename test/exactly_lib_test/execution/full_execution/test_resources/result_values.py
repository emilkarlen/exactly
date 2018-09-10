from exactly_lib.execution import phase_step
from exactly_lib.execution.failure_info import PhaseFailureInfo
from exactly_lib.execution.full_execution.result import FullExeResultStatus, FullExeResult
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.failure_details import new_failure_details_from_message

DUMMY_SDS = SandboxDirectoryStructure('test-root-dir')


def full_result_with_failure_info(status: FullExeResultStatus,
                                  failure_phase_step=phase_step.ASSERT__MAIN) -> FullExeResult:
    return FullExeResult(status,
                         DUMMY_SDS,
                         None,
                         PhaseFailureInfo(failure_phase_step,
                                          new_failure_details_from_message(
                                              'failure message')))


def full_result_without_failure_info(status: FullExeResultStatus) -> FullExeResult:
    return FullExeResult(status,
                         DUMMY_SDS,
                         None,
                         None)


FULL_RESULT_XFAIL = full_result_with_failure_info(FullExeResultStatus.XFAIL)
FULL_RESULT_XPASS = full_result_without_failure_info(FullExeResultStatus.XPASS)
FULL_RESULT_HARD_ERROR = full_result_with_failure_info(FullExeResultStatus.HARD_ERROR)
FULL_RESULT_VALIDATE = full_result_with_failure_info(FullExeResultStatus.VALIDATION_ERROR)
FULL_RESULT_IMPLEMENTATION_ERROR = full_result_with_failure_info(FullExeResultStatus.IMPLEMENTATION_ERROR)
