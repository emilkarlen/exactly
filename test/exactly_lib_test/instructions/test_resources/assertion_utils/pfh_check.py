from exactly_lib.test_case.phases.result import pfh
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


def status_is(expected_status: pfh.PassOrFailOrHardErrorEnum) -> va.ValueAssertion:
    return va.sub_component('status',
                            pfh.PassOrFailOrHardError.status.fget,
                            va.Equals(expected_status)
                            )


def is_pass() -> va.ValueAssertion:
    return status_is(pfh.PassOrFailOrHardErrorEnum.PASS)


def is_fail() -> va.ValueAssertion:
    return status_is(pfh.PassOrFailOrHardErrorEnum.FAIL)


def is_hard_error() -> va.ValueAssertion:
    return status_is(pfh.PassOrFailOrHardErrorEnum.HARD_ERROR)


def not_applicable() -> va.ValueAssertion:
    return va.Constant(False, 'Not applicable')
