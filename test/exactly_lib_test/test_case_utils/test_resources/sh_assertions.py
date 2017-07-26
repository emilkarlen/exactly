from exactly_lib.test_case.phases.result import sh
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def is_success() -> asrt.ValueAssertion:
    return asrt.OnTransformed(lambda value: value.is_success,
                              asrt.Boolean(True,
                                           'Status is expected to be success'))


def is_hard_error(assertion_on_error_message: asrt.ValueAssertion = asrt.anything_goes()) -> asrt.ValueAssertion:
    return asrt.And([
        asrt.OnTransformed(lambda value: value.is_hard_error,
                           asrt.Boolean(True,
                                        'Status is expected to be hard-error')),
        asrt.sub_component('error message',
                           sh.SuccessOrHardError.failure_message.fget,
                           assertion_on_error_message)
    ])


def is_sh_and(assertion: asrt.ValueAssertion) -> asrt.ValueAssertion:
    return asrt.And([asrt.IsInstance(sh.SuccessOrHardError),
                     assertion])
