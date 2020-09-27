"""
ValueAssertion:s on PartialExeResult
"""

from typing import Optional

from exactly_lib.execution.failure_info import FailureInfo
from exactly_lib.execution.partial_execution.result import PartialExeResult
from exactly_lib.execution.result import ActionToCheckOutcome, ExecutionFailureStatus
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib_test.execution.test_resources import result_assertions as asrt_atc
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def is_pass(sds: ValueAssertion[Optional[SandboxDs]] =
            asrt.is_instance(SandboxDs),
            action_to_check_outcome: ValueAssertion[Optional[ActionToCheckOutcome]] =
            asrt.is_instance(ActionToCheckOutcome)
            ) -> ValueAssertion[PartialExeResult]:
    return matches(status=asrt.is_(None),
                   failure_info=asrt.is_none,
                   has_sds=asrt.equals(True),
                   sds=sds,
                   action_to_check_outcome=action_to_check_outcome,
                   has_action_to_check_outcome=asrt.equals(True),
                   )


def is_failure(status: ExecutionFailureStatus,
               failure_info: ValueAssertion[Optional[FailureInfo]] = asrt.is_instance(FailureInfo),
               sds: ValueAssertion[Optional[SandboxDs]] = asrt.anything_goes(),
               has_sds: ValueAssertion[bool] = asrt.anything_goes(),
               action_to_check_outcome: ValueAssertion[Optional[ActionToCheckOutcome]] = asrt.anything_goes(),
               has_action_to_check_outcome: ValueAssertion[bool] = asrt.anything_goes(),
               ) -> ValueAssertion[PartialExeResult]:
    return matches(status=asrt.is_(status),
                   sds=sds,
                   has_sds=has_sds,
                   action_to_check_outcome=action_to_check_outcome,
                   has_action_to_check_outcome=has_action_to_check_outcome,
                   failure_info=failure_info)


def status_is(expected: ExecutionFailureStatus) -> ValueAssertion[PartialExeResult]:
    return matches(status=asrt.is_(expected))


def has_no_sds() -> ValueAssertion[PartialExeResult]:
    return matches(
        has_sds=asrt.equals(False),
        sds=asrt.is_none,
    )


def has_sds(sds: ValueAssertion[SandboxDs] =
            asrt.is_instance(SandboxDs)) -> ValueAssertion[PartialExeResult]:
    return matches(
        has_sds=asrt.equals(True),
        sds=asrt.is_instance_with(SandboxDs, sds),
    )


def has_no_action_to_check_outcome() -> ValueAssertion[PartialExeResult]:
    return matches(
        has_action_to_check_outcome=asrt.equals(False),
        action_to_check_outcome=asrt.is_none,
    )


def has_action_to_check_outcome(action_to_check_outcome: ValueAssertion[ActionToCheckOutcome] =
                                asrt.is_instance(ActionToCheckOutcome)) -> ValueAssertion[PartialExeResult]:
    return matches(
        has_action_to_check_outcome=asrt.equals(True),
        action_to_check_outcome=asrt.is_instance_with(ActionToCheckOutcome, action_to_check_outcome),
    )


def has_action_to_check_outcome_with_exit_code(exit_code: int) -> ValueAssertion[PartialExeResult]:
    return has_action_to_check_outcome(asrt_atc.is_exit_code(exit_code))


def matches2(status: Optional[ExecutionFailureStatus],
             sds: ValueAssertion[PartialExeResult],
             action_to_check_outcome: ValueAssertion[PartialExeResult],
             failure_info: ValueAssertion[Optional[FailureInfo]] = asrt.anything_goes()
             ) -> ValueAssertion[PartialExeResult]:
    return asrt.and_([
        matches(status=asrt.is_(status),
                failure_info=failure_info),
        sds,
        action_to_check_outcome,
    ])


def matches(
        status: ValueAssertion[Optional[ExecutionFailureStatus]] = asrt.anything_goes(),
        has_sds: ValueAssertion[bool] = asrt.anything_goes(),
        sds: ValueAssertion[Optional[SandboxDs]] = asrt.anything_goes(),
        has_action_to_check_outcome: ValueAssertion[bool] = asrt.anything_goes(),
        action_to_check_outcome: ValueAssertion[Optional[ActionToCheckOutcome]] = asrt.anything_goes(),
        failure_info: ValueAssertion[Optional[FailureInfo]] = asrt.anything_goes(),
) -> ValueAssertion[PartialExeResult]:
    return asrt.and_([
        asrt.sub_component('status',
                           PartialExeResult.status.fget,
                           status),
        asrt.sub_component('has_sds',
                           PartialExeResult.has_sds.fget,
                           has_sds),
        asrt.sub_component('sds',
                           PartialExeResult.sds.fget,
                           sds),
        asrt.sub_component('has_action_to_check_outcome',
                           PartialExeResult.has_action_to_check_outcome.fget,
                           has_action_to_check_outcome),
        asrt.sub_component('action_to_check_outcome',
                           PartialExeResult.action_to_check_outcome.fget,
                           action_to_check_outcome),
        asrt.sub_component('failure_info',
                           PartialExeResult.failure_info.fget,
                           failure_info),
    ])
