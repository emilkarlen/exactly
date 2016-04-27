from exactly_lib.test_case.phases.result import sh
from exactly_lib_test.test_resources import value_assertion as va


def is_success() -> va.ValueAssertion:
    return va.OnTransformed(lambda value: value.is_success,
                            va.Boolean(True,
                                       'Status is expected to be success'))


def is_hard_error() -> va.ValueAssertion:
    return va.OnTransformed(lambda value: value.is_hard_error,
                            va.Boolean(True,
                                       'Status is expected to be hard-error'))


def is_sh_and(assertion: va.ValueAssertion) -> va.ValueAssertion:
    return va.And([va.IsInstance(sh.SuccessOrHardError),
                   assertion])
