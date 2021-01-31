"""
ValueAssertion:s on FullExeResult
"""
from typing import Optional

from exactly_lib.execution.failure_info import FailureInfo
from exactly_lib.execution.full_execution.result import FullExeResultStatus, FullExeResult
from exactly_lib.execution.result import ActionToCheckOutcome
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib_test.execution.test_resources import result_assertions as asrt_atc
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def is_pass(sds: Assertion[Optional[SandboxDs]] =
            asrt.is_instance(SandboxDs),
            action_to_check_outcome: Assertion[Optional[ActionToCheckOutcome]] =
            asrt.is_instance(ActionToCheckOutcome)
            ) -> Assertion[FullExeResult]:
    return matches(status=asrt.is_(FullExeResultStatus.PASS),
                   failure_info=asrt.is_none,
                   has_sds=asrt.equals(True),
                   sds=sds,
                   has_action_to_check_outcome=asrt.equals(True),
                   action_to_check_outcome=action_to_check_outcome)


def is_xpass(sds: Assertion[Optional[SandboxDs]] =
             asrt.is_instance(SandboxDs),
             action_to_check_outcome: Assertion[Optional[ActionToCheckOutcome]] =
             asrt.is_instance(ActionToCheckOutcome)
             ) -> Assertion[FullExeResult]:
    return matches(status=asrt.is_(FullExeResultStatus.XPASS),
                   failure_info=asrt.is_none,
                   has_sds=asrt.equals(True),
                   sds=sds,
                   has_action_to_check_outcome=asrt.equals(True),
                   action_to_check_outcome=action_to_check_outcome)


def is_skipped() -> Assertion[FullExeResult]:
    return matches(status=asrt.is_(FullExeResultStatus.SKIPPED),
                   failure_info=asrt.is_none,
                   has_sds=asrt.equals(False),
                   sds=asrt.is_none,
                   has_action_to_check_outcome=asrt.equals(False),
                   action_to_check_outcome=asrt.is_none)


def is_failure(status: FullExeResultStatus,
               failure_info: Assertion[Optional[FailureInfo]] = asrt.is_instance(FailureInfo),
               sds: Assertion[Optional[SandboxDs]] = asrt.anything_goes(),
               action_to_check_outcome: Assertion[Optional[ActionToCheckOutcome]] = asrt.anything_goes(),
               ) -> Assertion[FullExeResult]:
    return matches(status=asrt.is_(status),
                   sds=sds,
                   action_to_check_outcome=action_to_check_outcome,
                   failure_info=failure_info)


def has_no_sds() -> Assertion[FullExeResult]:
    return matches(
        has_sds=asrt.equals(False),
        sds=asrt.is_none,
    )


def has_sds(sds: Assertion[SandboxDs] =
            asrt.is_instance(SandboxDs)) -> Assertion[FullExeResult]:
    return matches(
        has_sds=asrt.equals(True),
        sds=asrt.is_instance_with(SandboxDs, sds),
    )


def has_no_action_to_check_outcome() -> Assertion[FullExeResult]:
    return matches(
        has_action_to_check_outcome=asrt.equals(False),
        action_to_check_outcome=asrt.is_none,
    )


def has_action_to_check_outcome(action_to_check_outcome: Assertion[ActionToCheckOutcome] =
                                asrt.is_instance(ActionToCheckOutcome)) -> Assertion[FullExeResult]:
    return matches(
        has_action_to_check_outcome=asrt.equals(True),
        action_to_check_outcome=asrt.is_instance_with(ActionToCheckOutcome, action_to_check_outcome),
    )


def has_action_to_check_outcome_with_exit_code(exit_code: int) -> Assertion[FullExeResult]:
    return has_action_to_check_outcome(asrt_atc.is_exit_code(exit_code))


def matches2(status: FullExeResultStatus,
             sds: Assertion[FullExeResult],
             action_to_check_outcome: Assertion[FullExeResult],
             failure_info: Assertion[Optional[FailureInfo]] = asrt.anything_goes()
             ) -> Assertion[FullExeResult]:
    return asrt.and_([
        matches(status=asrt.is_(status),
                failure_info=failure_info),
        sds,
        action_to_check_outcome,
    ])


def matches(
        status: Assertion[FullExeResultStatus] = asrt.anything_goes(),
        has_sds: Assertion[bool] = asrt.anything_goes(),
        sds: Assertion[Optional[SandboxDs]] = asrt.anything_goes(),
        has_action_to_check_outcome: Assertion[bool] = asrt.anything_goes(),
        action_to_check_outcome: Assertion[Optional[ActionToCheckOutcome]] = asrt.anything_goes(),
        failure_info: Assertion[Optional[FailureInfo]] = asrt.anything_goes(),
) -> Assertion[FullExeResult]:
    return asrt.is_instance_with__many(
        FullExeResult,
        [
            asrt.sub_component('status',
                               FullExeResult.status.fget,
                               status),
            asrt.sub_component('has_sds',
                               FullExeResult.has_sds.fget,
                               has_sds),
            asrt.sub_component('sds',
                               FullExeResult.sds.fget,
                               sds),
            asrt.sub_component('has_action_to_check_outcome',
                               FullExeResult.has_action_to_check_outcome.fget,
                               has_action_to_check_outcome),
            asrt.sub_component('action_to_check_outcome',
                               FullExeResult.action_to_check_outcome.fget,
                               action_to_check_outcome),
            asrt.sub_component('failure_info',
                               FullExeResult.failure_info.fget,
                               failure_info),
        ])
