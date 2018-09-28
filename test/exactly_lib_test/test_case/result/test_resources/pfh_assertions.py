from exactly_lib.test_case.result import pfh
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def status_is(expected_status: pfh.PassOrFailOrHardErrorEnum) -> ValueAssertion[pfh.PassOrFailOrHardError]:
    return asrt.sub_component('status',
                              pfh.PassOrFailOrHardError.status.fget,
                              asrt.Equals(expected_status)
                              )


def is_pass() -> ValueAssertion[pfh.PassOrFailOrHardError]:
    return status_is(pfh.PassOrFailOrHardErrorEnum.PASS)


def is_fail(assertion_on_error_message: ValueAssertion = asrt.is_instance(str)
            ) -> ValueAssertion[pfh.PassOrFailOrHardError]:
    return asrt.And([
        status_is(pfh.PassOrFailOrHardErrorEnum.FAIL),
        failure_message_is(assertion_on_error_message)
    ])


def is_hard_error(assertion_on_error_message: ValueAssertion = asrt.is_instance(str)
                  ) -> ValueAssertion[pfh.PassOrFailOrHardError]:
    return asrt.And([
        status_is(pfh.PassOrFailOrHardErrorEnum.HARD_ERROR),
        failure_message_is(assertion_on_error_message)
    ])


def failure_message_is(assertion_on_error_message: ValueAssertion
                       ) -> ValueAssertion[pfh.PassOrFailOrHardError]:
    return asrt.sub_component('failure message',
                              pfh.PassOrFailOrHardError.failure_message.fget,
                              assertion_on_error_message)
