"""
ValueAssertion:s on FullExeResult
"""
from typing import Optional

from exactly_lib.execution.failure_info import FailureInfo
from exactly_lib.execution.full_execution.result import FullExeResultStatus, FullExeResult
from exactly_lib.execution.result import ActionToCheckOutcome
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def is_pass(sds: asrt.ValueAssertion[Optional[SandboxDirectoryStructure]] =
            asrt.is_instance(SandboxDirectoryStructure),
            action_to_check_outcome: asrt.ValueAssertion[Optional[ActionToCheckOutcome]] =
            asrt.is_instance(ActionToCheckOutcome)
            ) -> asrt.ValueAssertion[FullExeResult]:
    return matches(status=asrt.is_(FullExeResultStatus.PASS),
                   failure_info=asrt.is_none,
                   sds=sds,
                   action_to_check_outcome=action_to_check_outcome)


def is_xpass(sds: asrt.ValueAssertion[Optional[SandboxDirectoryStructure]] =
             asrt.is_instance(SandboxDirectoryStructure),
             action_to_check_outcome: asrt.ValueAssertion[Optional[ActionToCheckOutcome]] =
             asrt.is_instance(ActionToCheckOutcome)
             ) -> asrt.ValueAssertion[FullExeResult]:
    return matches(status=asrt.is_(FullExeResultStatus.XPASS),
                   failure_info=asrt.is_none,
                   sds=sds,
                   action_to_check_outcome=action_to_check_outcome)


def is_skipped() -> asrt.ValueAssertion[FullExeResult]:
    return matches(status=asrt.is_(FullExeResultStatus.SKIPPED),
                   failure_info=asrt.is_none,
                   sds=asrt.is_none,
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


def matches(
        status: asrt.ValueAssertion[FullExeResultStatus] = asrt.anything_goes(),
        sds: asrt.ValueAssertion[Optional[SandboxDirectoryStructure]] = asrt.anything_goes(),
        action_to_check_outcome: asrt.ValueAssertion[Optional[ActionToCheckOutcome]] = asrt.anything_goes(),
        failure_info: asrt.ValueAssertion[Optional[FailureInfo]] = asrt.anything_goes(),
) -> asrt.ValueAssertion[FullExeResult]:
    return asrt.and_([
        asrt.sub_component('status',
                           FullExeResult.status.fget,
                           status),
        asrt.sub_component('sds',
                           FullExeResult.sds.fget,
                           sds),
        asrt.sub_component('action_to_check_outcome',
                           FullExeResult.action_to_check_outcome.fget,
                           action_to_check_outcome),
        asrt.sub_component('failure_info',
                           FullExeResult.failure_info.fget,
                           failure_info),
    ])
