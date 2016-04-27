from exactly_lib.test_case.phases.result import svh
from exactly_lib_test.test_resources import value_assertion as va


def status_is(expected_status: svh.SuccessOrValidationErrorOrHardErrorEnum) -> va.ValueAssertion:
    return va.sub_component('status',
                            svh.SuccessOrValidationErrorOrHardError.status.fget,
                            va.Equals(expected_status)
                            )


def is_success():
    return status_is(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS)


def is_hard_error():
    return status_is(svh.SuccessOrValidationErrorOrHardErrorEnum.HARD_ERROR)


def is_validation_error():
    return status_is(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR)


def is_svh_and(assertion: va.ValueAssertion) -> va.ValueAssertion:
    return va.And([va.IsInstance(svh.SuccessOrValidationErrorOrHardError),
                   assertion])


def not_applicable() -> va.ValueAssertion:
    return va.Constant(False, 'Not applicable')
