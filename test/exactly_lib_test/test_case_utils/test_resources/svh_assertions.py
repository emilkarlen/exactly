import unittest

from exactly_lib.test_case.phases.result import svh
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder


def status_is(expected_status: svh.SuccessOrValidationErrorOrHardErrorEnum) -> asrt.ValueAssertion:
    return asrt.sub_component('status',
                              svh.SuccessOrValidationErrorOrHardError.status.fget,
                              asrt.Equals(expected_status)
                              )


def status_is_not_success(expected_status: svh.SuccessOrValidationErrorOrHardErrorEnum,
                          assertion_on_error_message: asrt.ValueAssertion) -> asrt.ValueAssertion:
    return asrt.And([
        status_is(expected_status),
        asrt.sub_component('error message',
                           svh.SuccessOrValidationErrorOrHardError.failure_message.fget,
                           assertion_on_error_message)
    ])


def is_success() -> asrt.ValueAssertion:
    return _IsSuccess()


class _IsSuccess(asrt.ValueAssertion):
    def __init__(self):
        pass

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: MessageBuilder = MessageBuilder()):
        put.assertIsInstance(value, svh.SuccessOrValidationErrorOrHardError)
        if not value.is_success:
            put.fail('\n'.join([
                'Expected: ' + svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS.name,
                'Actual  : {st}: {msg}'.format(
                    st=value.status.name,
                    msg=repr(value.failure_message))
            ]))


def is_hard_error(assertion_on_error_message: asrt.ValueAssertion = asrt.is_instance(str)) -> asrt.ValueAssertion:
    return status_is_not_success(svh.SuccessOrValidationErrorOrHardErrorEnum.HARD_ERROR,
                                 assertion_on_error_message)


def is_validation_error(assertion_on_error_message: asrt.ValueAssertion = asrt.is_instance(str)) -> asrt.ValueAssertion:
    return status_is_not_success(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                                 assertion_on_error_message)


def is_svh_and(assertion: asrt.ValueAssertion) -> asrt.ValueAssertion:
    return asrt.And([asrt.IsInstance(svh.SuccessOrValidationErrorOrHardError),
                     assertion])
