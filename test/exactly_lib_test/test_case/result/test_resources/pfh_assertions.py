from exactly_lib.test_case.result import pfh
from exactly_lib_test.common.test_resources import text_docs
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.test_resources import file_printable_assertions as asrt_file_printable


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


def is_hard_error(assertion_on_error_message: ValueAssertion[str] = asrt.is_instance(str)
                  ) -> ValueAssertion[pfh.PassOrFailOrHardError]:
    return asrt.And([
        status_is(pfh.PassOrFailOrHardErrorEnum.HARD_ERROR),
        failure_message_is(assertion_on_error_message)
    ])


def failure_message_is(assertion_on_error_message: ValueAssertion[str]
                       ) -> ValueAssertion[pfh.PassOrFailOrHardError]:
    return asrt.with_sub_component_message(
        'failure message',
        asrt.and_([
            asrt.sub_component(
                'text-doc',
                pfh.PassOrFailOrHardError.failure_message__td.fget,
                text_docs.is_single_pre_formatted_text(assertion_on_error_message)
            ),
            asrt.sub_component(
                'file-printer',
                pfh.PassOrFailOrHardError.failure_message.fget,
                asrt_file_printable.matches(assertion_on_error_message)
            ),
        ])
    )
