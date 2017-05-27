from exactly_lib.test_case.phases.result import pfh
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def status_is(expected_status: pfh.PassOrFailOrHardErrorEnum) -> asrt.ValueAssertion:
    return asrt.sub_component('status',
                              pfh.PassOrFailOrHardError.status.fget,
                              asrt.Equals(expected_status)
                              )


def is_pass() -> asrt.ValueAssertion:
    return status_is(pfh.PassOrFailOrHardErrorEnum.PASS)


def is_fail(assertion_on_error_message: asrt.ValueAssertion = asrt.anything_goes()) -> asrt.ValueAssertion:
    return asrt.And([
        status_is(pfh.PassOrFailOrHardErrorEnum.FAIL),
        failure_message_is(assertion_on_error_message)
    ])


def is_hard_error(assertion_on_error_message: asrt.ValueAssertion = asrt.anything_goes()) -> asrt.ValueAssertion:
    return asrt.And([
        status_is(pfh.PassOrFailOrHardErrorEnum.HARD_ERROR),
        failure_message_is(assertion_on_error_message)
    ])


def failure_message_is(assertion_on_error_message: asrt.ValueAssertion) -> asrt.ValueAssertion:
    return asrt.sub_component('failure message',
                            pfh.PassOrFailOrHardError.failure_message.fget,
                            assertion_on_error_message)
