"""
ValueAssertion:s on ExitCodeOrHardError
"""
from exactly_lib.test_case.result.eh import ExitCodeOrHardError
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion

is_any_exit_code = asrt.OnTransformed(lambda value: value.is_exit_code,
                                      asrt.Boolean(True,
                                                   'Value is expected to represent an exit code (not a hard error)'))


def is_exit_code(expected_exit_code: int) -> ValueAssertion[ExitCodeOrHardError]:
    return asrt.And([
        is_any_exit_code,
        asrt.sub_component(
            'exit_code',
            ExitCodeOrHardError.exit_code.fget,
            asrt.equals(expected_exit_code)
        ),
    ])


is_hard_error = asrt.OnTransformed(lambda value: value.is_hard_error,
                                   asrt.Boolean(True,
                                                'Status is expected to be hard error'))
