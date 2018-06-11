from exactly_lib.execution.partial_execution.result import PartialExeResultStatus, PartialExeResult
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def partial_result_status_is(expected: PartialExeResultStatus) -> asrt.ValueAssertion[PartialExeResult]:
    return asrt.is_instance_with(PartialExeResult,
                                 asrt.sub_component('status',
                                                    PartialExeResult.status.fget,
                                                    asrt.equals(expected)))
