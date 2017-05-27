"""
ValueAssertion:s on ExitCodeOrHardError
"""

from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt

is_any_exit_code = asrt.OnTransformed(lambda value: value.is_exit_code,
                                      asrt.Boolean(True,
                                               'Value is expected to represent an exit code (not a hard error)'))


def is_exit_code(expected_exit_code: int) -> asrt.ValueAssertion:
    return asrt.And([
        is_any_exit_code,
        asrt.OnTransformed(lambda value: value.exit_code,
                           asrt.Equals(expected_exit_code,
                                   'Exit code value')),
    ])


is_hard_error = asrt.OnTransformed(lambda value: value.is_hard_error,
                                   asrt.Boolean(True,
                                            'Status is expected to be hard error'))
