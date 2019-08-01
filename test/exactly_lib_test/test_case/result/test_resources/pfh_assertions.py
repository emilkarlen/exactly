from exactly_lib.test_case.result import pfh
from exactly_lib_test.common.test_resources import text_docs
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.simple_textstruct.test_resources import renderer_assertions as asrt_renderer


def status_is(expected_status: pfh.PassOrFailOrHardErrorEnum) -> ValueAssertion[pfh.PassOrFailOrHardError]:
    return asrt.sub_component('status',
                              pfh.PassOrFailOrHardError.status.fget,
                              asrt.Equals(expected_status)
                              )


def is_pass() -> ValueAssertion[pfh.PassOrFailOrHardError]:
    return status_is(pfh.PassOrFailOrHardErrorEnum.PASS)


def is_fail(assertion_on_error_message: ValueAssertion[str] = asrt.is_instance(str)
            ) -> ValueAssertion[pfh.PassOrFailOrHardError]:
    return asrt.And([
        status_is(pfh.PassOrFailOrHardErrorEnum.FAIL),
        failure_message_is(assertion_on_error_message)
    ])


def is_fail__with_arbitrary_message() -> ValueAssertion[pfh.PassOrFailOrHardError]:
    return asrt.And([
        status_is(pfh.PassOrFailOrHardErrorEnum.FAIL),
        failure_message_is_present_and_valid()
    ])


def is_hard_error(assertion_on_error_message: ValueAssertion[str] = asrt.is_instance(str)
                  ) -> ValueAssertion[pfh.PassOrFailOrHardError]:
    return asrt.And([
        status_is(pfh.PassOrFailOrHardErrorEnum.HARD_ERROR),
        failure_message_is(assertion_on_error_message)
    ])


def is_hard_error__with_arbitrary_message() -> ValueAssertion[pfh.PassOrFailOrHardError]:
    return asrt.And([
        status_is(pfh.PassOrFailOrHardErrorEnum.HARD_ERROR),
        failure_message_is_present_and_valid()
    ])


def failure_message_is(assertion_on_error_message: ValueAssertion[str]
                       ) -> ValueAssertion[pfh.PassOrFailOrHardError]:
    return asrt.sub_component(
        'failure message',
        pfh.PassOrFailOrHardError.failure_message__td.fget,
        text_docs.is_single_pre_formatted_text(assertion_on_error_message)
    )


def failure_message_is_present_and_valid() -> ValueAssertion[pfh.PassOrFailOrHardError]:
    return asrt.sub_component(
        'failure message',
        pfh.PassOrFailOrHardError.failure_message__td.fget,
        asrt.is_not_none_and(asrt_renderer.is_renderer_of_major_blocks())
    )
