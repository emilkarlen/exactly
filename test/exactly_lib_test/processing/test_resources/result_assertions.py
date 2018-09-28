from exactly_lib.execution.full_execution.result import FullExeResultStatus
from exactly_lib.processing.test_case_processing import Status, AccessErrorType, Result
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def result_matches(status: Status,
                   access_error_type: AccessErrorType) -> ValueAssertion[Result]:
    return asrt.and_([
        asrt.sub_component('status',
                           Result.status.fget,
                           asrt.equals(status)),
        asrt.sub_component('access_error_type',
                           Result.access_error_type.fget,
                           asrt.equals(access_error_type)),
    ])


def result_for_executed_status_matches(full_result_status: FullExeResultStatus) -> ValueAssertion[Result]:
    def get_full_result_status(result: Result) -> FullExeResultStatus:
        return result.execution_result.status

    return asrt.and_([
        asrt.sub_component('status',
                           Result.status.fget,
                           asrt.equals(Status.EXECUTED)),
        asrt.sub_component('full_result/status',
                           get_full_result_status,
                           asrt.equals(full_result_status)),
    ])
