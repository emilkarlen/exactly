from exactly_lib.test_case.phases.result import svh
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


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
    return status_is(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS)


def is_hard_error(assertion_on_error_message: asrt.ValueAssertion = asrt.anything_goes()) -> asrt.ValueAssertion:
    return status_is_not_success(svh.SuccessOrValidationErrorOrHardErrorEnum.HARD_ERROR,
                                 assertion_on_error_message)


def is_validation_error(assertion_on_error_message: asrt.ValueAssertion = asrt.anything_goes()) -> asrt.ValueAssertion:
    return status_is_not_success(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                                 assertion_on_error_message)


def is_svh_and(assertion: asrt.ValueAssertion) -> asrt.ValueAssertion:
    return asrt.And([asrt.IsInstance(svh.SuccessOrValidationErrorOrHardError),
                   assertion])
