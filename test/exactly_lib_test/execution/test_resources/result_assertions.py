from typing import Optional

from exactly_lib.execution.result import ActionToCheckOutcome
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def action_to_check_has_executed_completely(exit_code: int) -> Assertion[Optional[ActionToCheckOutcome]]:
    return asrt.is_not_none_and_instance_with(ActionToCheckOutcome,
                                              matches(asrt.equals(exit_code)))


def matches(exit_code: Assertion[int] = asrt.anything_goes()) -> Assertion[ActionToCheckOutcome]:
    return asrt.is_instance_with(ActionToCheckOutcome,
                                 asrt.sub_component('exit_code',
                                                    ActionToCheckOutcome.exit_code.fget,
                                                    exit_code)
                                 )


def is_exit_code(exit_code: int) -> Assertion[ActionToCheckOutcome]:
    return matches(exit_code=asrt.equals(exit_code))
