from exactly_lib.test_case.phases.result import svh
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


def status_is(expected_status: svh.SuccessOrValidationErrorOrHardErrorEnum) -> va.ValueAssertion:
    return va.sub_component('status',
                            svh.SuccessOrValidationErrorOrHardError.status.fget,
                            va.Equals(expected_status)
                            )


def is_success() -> va.ValueAssertion:
    return status_is(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS)


def is_hard_error() -> va.ValueAssertion:
    return status_is(svh.SuccessOrValidationErrorOrHardErrorEnum.HARD_ERROR)


def is_validation_error() -> va.ValueAssertion:
    return status_is(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR)


def is_svh_and(assertion: va.ValueAssertion) -> va.ValueAssertion:
    return va.And([va.IsInstance(svh.SuccessOrValidationErrorOrHardError),
                   assertion])
