"""
ValueAssertion:s on PartialExeResult
"""

from typing import Optional

from exactly_lib.execution.failure_info import FailureInfo
from exactly_lib.execution.partial_execution.result import PartialExeResultStatus, PartialExeResult
from exactly_lib.execution.result import ActionToCheckOutcome
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.execution.test_resources import result_assertions as asrt_atc
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def is_pass(sds: asrt.ValueAssertion[Optional[SandboxDirectoryStructure]] =
            asrt.is_instance(SandboxDirectoryStructure),
            action_to_check_outcome: asrt.ValueAssertion[Optional[ActionToCheckOutcome]] =
            asrt.is_instance(ActionToCheckOutcome)
            ) -> asrt.ValueAssertion[PartialExeResult]:
    return matches(status=asrt.is_(PartialExeResultStatus.PASS),
                   failure_info=asrt.is_none,
                   has_sds=asrt.equals(True),
                   sds=sds,
                   action_to_check_outcome=action_to_check_outcome,
                   has_action_to_check_outcome=asrt.equals(True),
                   )


def is_failure(status: PartialExeResultStatus,
               failure_info: asrt.ValueAssertion[Optional[FailureInfo]] = asrt.is_instance(FailureInfo),
               sds: asrt.ValueAssertion[Optional[SandboxDirectoryStructure]] = asrt.anything_goes(),
               has_sds: asrt.ValueAssertion[bool] = asrt.anything_goes(),
               action_to_check_outcome: asrt.ValueAssertion[Optional[ActionToCheckOutcome]] = asrt.anything_goes(),
               has_action_to_check_outcome: asrt.ValueAssertion[bool] = asrt.anything_goes(),
               ) -> asrt.ValueAssertion[PartialExeResult]:
    return matches(status=asrt.is_(status),
                   sds=sds,
                   has_sds=has_sds,
                   action_to_check_outcome=action_to_check_outcome,
                   has_action_to_check_outcome=has_action_to_check_outcome,
                   failure_info=failure_info)


def status_is(expected: PartialExeResultStatus) -> asrt.ValueAssertion[PartialExeResult]:
    return matches(status=asrt.is_(expected))


def has_no_sds() -> asrt.ValueAssertion[PartialExeResult]:
    return matches(
        has_sds=asrt.equals(False),
        sds=asrt.is_none,
    )


def has_sds(sds: asrt.ValueAssertion[SandboxDirectoryStructure] =
            asrt.is_instance(SandboxDirectoryStructure)) -> asrt.ValueAssertion[PartialExeResult]:
    return matches(
        has_sds=asrt.equals(True),
        sds=asrt.is_instance_with(SandboxDirectoryStructure, sds),
    )


def has_no_action_to_check_outcome() -> asrt.ValueAssertion[PartialExeResult]:
    return matches(
        has_action_to_check_outcome=asrt.equals(False),
        action_to_check_outcome=asrt.is_none,
    )


def has_action_to_check_outcome(action_to_check_outcome: asrt.ValueAssertion[ActionToCheckOutcome] =
                                asrt.is_instance(ActionToCheckOutcome)) -> asrt.ValueAssertion[PartialExeResult]:
    return matches(
        has_action_to_check_outcome=asrt.equals(True),
        action_to_check_outcome=asrt.is_instance_with(ActionToCheckOutcome, action_to_check_outcome),
    )


def has_action_to_check_outcome_with_exit_code(exit_code: int) -> asrt.ValueAssertion[PartialExeResult]:
    return has_action_to_check_outcome(asrt_atc.is_exit_code(exit_code))


def matches2(sds: asrt.ValueAssertion[PartialExeResult],
             action_to_check_outcome: asrt.ValueAssertion[PartialExeResult],
             other: asrt.ValueAssertion[PartialExeResult] = asrt.anything_goes()
             ) -> asrt.ValueAssertion[PartialExeResult]:
    return asrt.and_([
        other,
        sds,
        action_to_check_outcome,
    ])


def matches3(status: PartialExeResultStatus,
             sds: asrt.ValueAssertion[PartialExeResult],
             action_to_check_outcome: asrt.ValueAssertion[PartialExeResult],
             failure_info: asrt.ValueAssertion[Optional[FailureInfo]] = asrt.anything_goes()
             ) -> asrt.ValueAssertion[PartialExeResult]:
    return asrt.and_([
        matches(status=asrt.is_(status),
                failure_info=failure_info),
        sds,
        action_to_check_outcome,
    ])


def matches(
        status: asrt.ValueAssertion[PartialExeResultStatus] = asrt.anything_goes(),
        has_sds: asrt.ValueAssertion[bool] = asrt.anything_goes(),
        sds: asrt.ValueAssertion[Optional[SandboxDirectoryStructure]] = asrt.anything_goes(),
        has_action_to_check_outcome: asrt.ValueAssertion[bool] = asrt.anything_goes(),
        action_to_check_outcome: asrt.ValueAssertion[Optional[ActionToCheckOutcome]] = asrt.anything_goes(),
        failure_info: asrt.ValueAssertion[Optional[FailureInfo]] = asrt.anything_goes(),
) -> asrt.ValueAssertion[PartialExeResult]:
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
