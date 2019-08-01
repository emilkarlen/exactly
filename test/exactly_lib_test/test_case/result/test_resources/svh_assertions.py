import unittest

from exactly_lib.test_case.result import svh
from exactly_lib.util import file_printables
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder, ValueAssertionBase
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.test_resources import file_printable_assertions as asrt_file_printable


def status_is(expected_status: svh.SuccessOrValidationErrorOrHardErrorEnum) -> ValueAssertion:
    return asrt.sub_component('status',
                              svh.SuccessOrValidationErrorOrHardError.status.fget,
                              asrt.Equals(expected_status)
                              )


def status_is_not_success(expected_status: svh.SuccessOrValidationErrorOrHardErrorEnum,
                          assertion_on_error_message: ValueAssertion[str] = asrt.is_instance(str)
                          ) -> ValueAssertion[svh.SuccessOrValidationErrorOrHardError]:
    return asrt.And([
        status_is(expected_status),
        asrt.with_sub_component_message(
            'error message',
            asrt.and_([
                asrt.sub_component(
                    'file-printable',
                    svh.SuccessOrValidationErrorOrHardError.failure_message.fget,
                    asrt_file_printable.matches(assertion_on_error_message)
                ),
                asrt.sub_component(
                    'text-doc',
                    svh.SuccessOrValidationErrorOrHardError.failure_message__td.fget,
                    asrt_text_doc.is_single_pre_formatted_text(assertion_on_error_message)
                ),
            ])
        )
    ])


def is_success() -> ValueAssertion[svh.SuccessOrValidationErrorOrHardError]:
    return _IsSuccess()


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
                    msg=repr(file_printables.print_to_string(value.failure_message)))
            ]))


def is_hard_error(assertion_on_error_message: ValueAssertion[str] = asrt.is_instance(str)
                  ) -> ValueAssertion[svh.SuccessOrValidationErrorOrHardError]:
    return status_is_not_success(svh.SuccessOrValidationErrorOrHardErrorEnum.HARD_ERROR,
                                 assertion_on_error_message)


def is_any_hard_error() -> ValueAssertion[svh.SuccessOrValidationErrorOrHardError]:
    return is_hard_error(asrt.is_instance(str))


def is_validation_error(assertion_on_error_message: ValueAssertion[str] = asrt.is_instance(str)
                        ) -> ValueAssertion[svh.SuccessOrValidationErrorOrHardError]:
    return status_is_not_success(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                                 assertion_on_error_message)


def is_any_validation_error() -> ValueAssertion[svh.SuccessOrValidationErrorOrHardError]:
    return is_validation_error(asrt.is_instance(str))


def is_svh_and(assertion: ValueAssertion[svh.SuccessOrValidationErrorOrHardError]
               ) -> ValueAssertion[svh.SuccessOrValidationErrorOrHardError]:
    return asrt.And([asrt.IsInstance(svh.SuccessOrValidationErrorOrHardError),
                     assertion])
