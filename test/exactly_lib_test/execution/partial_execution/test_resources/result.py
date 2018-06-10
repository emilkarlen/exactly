from exactly_lib.execution.partial_execution.result import PartialResultStatus, PartialResult
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def partial_result_status_is(expected: PartialResultStatus) -> asrt.ValueAssertion[PartialResult]:
    return asrt.is_instance_with(PartialResult,
                                 asrt.sub_component('status',
                                                    PartialResult.status.fget,
                                                    asrt.equals(expected)))
