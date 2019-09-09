import unittest

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case.result import svh
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder, ValueAssertionBase
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.simple_textstruct.test_resources import render_to_str


def status_is(expected_status: svh.SuccessOrValidationErrorOrHardErrorEnum) -> ValueAssertion:
    return asrt.sub_component('status',
                              svh.SuccessOrValidationErrorOrHardError.status.fget,
                              asrt.Equals(expected_status)
                              )


def status_is_not_success(expected_status: svh.SuccessOrValidationErrorOrHardErrorEnum,
                          error_message: ValueAssertion[TextRenderer] = asrt_text_doc.is_any_text()
                          ) -> ValueAssertion[svh.SuccessOrValidationErrorOrHardError]:
    return asrt.and_([
        status_is(expected_status),
        asrt.sub_component(
            'failure_message',
            svh.SuccessOrValidationErrorOrHardError.failure_message.fget,
            error_message
        )
    ])


def is_success() -> ValueAssertion[svh.SuccessOrValidationErrorOrHardError]:
    return _IsSuccess()


def is_hard_error(assertion_on_error_message: ValueAssertion[TextRenderer] = asrt_text_doc.is_any_text()
                  ) -> ValueAssertion[svh.SuccessOrValidationErrorOrHardError]:
    return status_is_not_success(svh.SuccessOrValidationErrorOrHardErrorEnum.HARD_ERROR,
                                 assertion_on_error_message)


def is_validation_error(assertion_on_error_message: ValueAssertion[TextRenderer] = asrt_text_doc.is_any_text()
                        ) -> ValueAssertion[svh.SuccessOrValidationErrorOrHardError]:
    return status_is_not_success(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                                 assertion_on_error_message)


def is_svh_and(assertion: ValueAssertion[svh.SuccessOrValidationErrorOrHardError]
               ) -> ValueAssertion[svh.SuccessOrValidationErrorOrHardError]:
    return asrt.And([asrt.IsInstance(svh.SuccessOrValidationErrorOrHardError),
                     assertion])


class _IsSuccess(ValueAssertionBase):
    def __init__(self):
        pass

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: MessageBuilder):
        put.assertIsInstance(value, svh.SuccessOrValidationErrorOrHardError)
        if not value.is_success:
            put.fail('\n'.join([
                'Expected: ' + svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS.name,
                'Actual  : {st}: {msg}'.format(
                    st=value.status.name,
                    msg=repr(render_to_str.print_major_blocks(value.failure_message.render_sequence())))
            ]))
