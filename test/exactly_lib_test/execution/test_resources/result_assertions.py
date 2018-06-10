from typing import Optional

from exactly_lib.execution.result import ActionToCheckOutcome
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def action_to_check_has_not_executed_completely() -> asrt.ValueAssertion[Optional[ActionToCheckOutcome]]:
    return asrt.is_none


def action_to_check_has_executed_completely(exit_code: int) -> asrt.ValueAssertion[Optional[ActionToCheckOutcome]]:
    return asrt.is_not_none_and_instance_with(ActionToCheckOutcome,
                                              asrt.sub_component('exit_code',
                                                                 ActionToCheckOutcome.exit_code.fget,
                                                                 asrt.equals(exit_code)))


def action_to_check_has_executed_completely_iff_phase_is_after_act(
        is_after_act: bool,
        exit_code: int
) -> asrt.ValueAssertion[Optional[ActionToCheckOutcome]]:
    if is_after_act:
        return action_to_check_has_executed_completely(exit_code)
    else:
        return action_to_check_has_not_executed_completely()
