from exactly_lib.test_case.phases.result import sh
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def is_success() -> asrt.ValueAssertion:
    return is_sh_and(asrt.sub_component('is_success',
                                        sh.SuccessOrHardError.is_success.fget,
                                        asrt.equals(True,
                                                    'Status is expected to be success')))


def is_hard_error(assertion_on_error_message: asrt.ValueAssertion = asrt.anything_goes()) -> asrt.ValueAssertion:
    return is_sh_and(asrt.And([
        asrt.sub_component('is_hard_error',
                           sh.SuccessOrHardError.is_hard_error.fget,
                           asrt.equals(True,
                                       'Status is expected to be hard-error')),
        asrt.sub_component('error message',
                           sh.SuccessOrHardError.failure_message.fget,
                           assertion_on_error_message)
    ]))


def is_sh_and(assertion: asrt.ValueAssertion) -> asrt.ValueAssertion:
    return asrt.is_instance_with(sh.SuccessOrHardError, assertion)
