from exactly_lib_test.test_resources.value_assertions import value_assertion as va

is_any_exit_code = va.OnTransformed(lambda value: value.is_exit_code,
                                    va.Boolean(True,
                                               'Value is expected to represent an exit code (not a hard error)'))


def is_exit_code(expected_exit_code: int) -> va.ValueAssertion:
    return va.And([
        is_any_exit_code,
        va.OnTransformed(lambda value: value.exit_code,
                         va.Equals(expected_exit_code,
                                   'Exit code value')),
    ])


is_hard_error = va.OnTransformed(lambda value: value.is_hard_error,
                                 va.Boolean(True,
                                            'Status is expected to be hard error'))
