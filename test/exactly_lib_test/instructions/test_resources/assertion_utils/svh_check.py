from exactly_lib.test_case.phases.result import svh
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


def status_is(expected_status: svh.SuccessOrValidationErrorOrHardErrorEnum) -> va.ValueAssertion:
    return va.sub_component('status',
                            svh.SuccessOrValidationErrorOrHardError.status.fget,
                            va.Equals(expected_status)
                            )


def status_is_not_success(expected_status: svh.SuccessOrValidationErrorOrHardErrorEnum,
                          assertion_on_error_message: va.ValueAssertion) -> va.ValueAssertion:
    return va.And([
        status_is(expected_status),
        va.sub_component('error message',
                         svh.SuccessOrValidationErrorOrHardError.failure_message.fget,
                         assertion_on_error_message)
    ])


def is_success() -> va.ValueAssertion:
    return status_is(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS)


def is_hard_error(assertion_on_error_message: va.ValueAssertion = va.anything_goes()) -> va.ValueAssertion:
    return status_is_not_success(svh.SuccessOrValidationErrorOrHardErrorEnum.HARD_ERROR,
                                 assertion_on_error_message)


def is_validation_error(assertion_on_error_message: va.ValueAssertion = va.anything_goes()) -> va.ValueAssertion:
    return status_is_not_success(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                                 assertion_on_error_message)


def is_svh_and(assertion: va.ValueAssertion) -> va.ValueAssertion:
    return va.And([va.IsInstance(svh.SuccessOrValidationErrorOrHardError),
                   assertion])
