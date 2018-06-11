"""
ValueAssertion:s on FullExeResult
"""
from typing import Optional

from exactly_lib.execution.failure_info import FailureInfo
from exactly_lib.execution.full_execution.result import FullExeResultStatus, FullExeResult
from exactly_lib.execution.result import ActionToCheckOutcome
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.execution.test_resources import result_assertions as asrt_atc
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def is_pass(sds: asrt.ValueAssertion[Optional[SandboxDirectoryStructure]] =
            asrt.is_instance(SandboxDirectoryStructure),
            action_to_check_outcome: asrt.ValueAssertion[Optional[ActionToCheckOutcome]] =
            asrt.is_instance(ActionToCheckOutcome)
            ) -> asrt.ValueAssertion[FullExeResult]:
    return matches(status=asrt.is_(FullExeResultStatus.PASS),
                   failure_info=asrt.is_none,
                   has_sds=asrt.equals(True),
                   sds=sds,
                   has_action_to_check_outcome=asrt.equals(True),
                   action_to_check_outcome=action_to_check_outcome)


def is_xpass(sds: asrt.ValueAssertion[Optional[SandboxDirectoryStructure]] =
             asrt.is_instance(SandboxDirectoryStructure),
             action_to_check_outcome: asrt.ValueAssertion[Optional[ActionToCheckOutcome]] =
             asrt.is_instance(ActionToCheckOutcome)
             ) -> asrt.ValueAssertion[FullExeResult]:
    return matches(status=asrt.is_(FullExeResultStatus.XPASS),
                   failure_info=asrt.is_none,
                   has_sds=asrt.equals(True),
                   sds=sds,
                   has_action_to_check_outcome=asrt.equals(True),
                   action_to_check_outcome=action_to_check_outcome)


def is_skipped() -> asrt.ValueAssertion[FullExeResult]:
    return matches(status=asrt.is_(FullExeResultStatus.SKIPPED),
                   failure_info=asrt.is_none,
                   has_sds=asrt.equals(False),
                   sds=asrt.is_none,
                   has_action_to_check_outcome=asrt.equals(False),
                   action_to_check_outcome=asrt.is_none)


def is_failure(status: FullExeResultStatus,
               failure_info: asrt.ValueAssertion[Optional[FailureInfo]] = asrt.is_instance(FailureInfo),
               sds: asrt.ValueAssertion[Optional[SandboxDirectoryStructure]] = asrt.anything_goes(),
               action_to_check_outcome: asrt.ValueAssertion[Optional[ActionToCheckOutcome]] = asrt.anything_goes(),
               ) -> asrt.ValueAssertion[FullExeResult]:
    return matches(status=asrt.is_(status),
                   sds=sds,
                   action_to_check_outcome=action_to_check_outcome,
                   failure_info=failure_info)


def has_no_sds() -> asrt.ValueAssertion[FullExeResult]:
    return matches(
        has_sds=asrt.equals(False),
        sds=asrt.is_none,
    )


def has_sds(sds: asrt.ValueAssertion[SandboxDirectoryStructure] =
            asrt.is_instance(SandboxDirectoryStructure)) -> asrt.ValueAssertion[FullExeResult]:
    return matches(
        has_sds=asrt.equals(True),
        sds=asrt.is_instance_with(SandboxDirectoryStructure, sds),
    )


def has_no_action_to_check_outcome() -> asrt.ValueAssertion[FullExeResult]:
    return matches(
        has_action_to_check_outcome=asrt.equals(False),
        action_to_check_outcome=asrt.is_none,
    )


def has_action_to_check_outcome(action_to_check_outcome: asrt.ValueAssertion[ActionToCheckOutcome] =
                                asrt.is_instance(ActionToCheckOutcome)) -> asrt.ValueAssertion[FullExeResult]:
    return matches(
        has_action_to_check_outcome=asrt.equals(True),
        action_to_check_outcome=asrt.is_instance_with(ActionToCheckOutcome, action_to_check_outcome),
    )


def has_action_to_check_outcome_with_exit_code(exit_code: int) -> asrt.ValueAssertion[FullExeResult]:
    return has_action_to_check_outcome(asrt_atc.is_exit_code(exit_code))


def matches2(status: FullExeResultStatus,
             sds: asrt.ValueAssertion[FullExeResult],
             action_to_check_outcome: asrt.ValueAssertion[FullExeResult],
             failure_info: asrt.ValueAssertion[Optional[FailureInfo]] = asrt.anything_goes()
             ) -> asrt.ValueAssertion[FullExeResult]:
    return asrt.and_([
        matches(status=asrt.is_(status),
                failure_info=failure_info),
        sds,
        action_to_check_outcome,
    ])


def matches(
        status: asrt.ValueAssertion[FullExeResultStatus] = asrt.anything_goes(),
        has_sds: asrt.ValueAssertion[bool] = asrt.anything_goes(),
        sds: asrt.ValueAssertion[Optional[SandboxDirectoryStructure]] = asrt.anything_goes(),
        has_action_to_check_outcome: asrt.ValueAssertion[bool] = asrt.anything_goes(),
        action_to_check_outcome: asrt.ValueAssertion[Optional[ActionToCheckOutcome]] = asrt.anything_goes(),
        failure_info: asrt.ValueAssertion[Optional[FailureInfo]] = asrt.anything_goes(),
) -> asrt.ValueAssertion[FullExeResult]:
    return asrt.and_([
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
