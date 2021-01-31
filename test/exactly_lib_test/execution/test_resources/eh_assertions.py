"""
ValueAssertion:s on ExitCodeOrHardError
"""
from typing import Optional

from exactly_lib.test_case.result.eh import ExitCodeOrHardError
from exactly_lib.test_case.result.failure_details import FailureDetails
from exactly_lib_test.test_case.result.test_resources import failure_details_assertions as asrt_failure_details
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion

is_any_exit_code = asrt.OnTransformed(lambda value: value.is_exit_code,
                                      asrt.Boolean(True,
                                                   'Value is expected to represent an exit code (not a hard error)'))


def is_exit_code(expected_exit_code: int) -> Assertion[ExitCodeOrHardError]:
    return asrt.And([
        is_any_exit_code,
        asrt.sub_component(
            'exit_code',
            ExitCodeOrHardError.exit_code.fget,
            asrt.equals(expected_exit_code)
        ),
    ])


def matches_hard_error(failure_details: Assertion[Optional[FailureDetails]] =
                       asrt_failure_details.is_any_failure_message()) -> Assertion[ExitCodeOrHardError]:
    return asrt.is_instance_with__many(
        ExitCodeOrHardError,
        [
            asrt.sub_component(
                'is_hard_error',
                ExitCodeOrHardError.is_hard_error.fget,
                asrt.is_true,
            ),
            asrt.sub_component(
                'failure details',
                ExitCodeOrHardError.failure_details.fget,
                asrt.is_optional_instance_with(FailureDetails, failure_details),
            ),
        ]
    )


is_hard_error = matches_hard_error()
