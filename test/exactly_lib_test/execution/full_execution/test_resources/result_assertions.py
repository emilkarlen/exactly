"""
ValueAssertion:s on FullResult
"""
from typing import Optional

from exactly_lib.execution.failure_info import FailureInfo
from exactly_lib.execution.full_execution.result import FullResultStatus, FullResult
from exactly_lib.execution.result import ActionToCheckOutcome
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def is_pass() -> asrt.ValueAssertion[FullResult]:
    return matches(status=asrt.is_(FullResultStatus.PASS),
                   failure_info=asrt.is_none,
                   sds=asrt.is_instance(SandboxDirectoryStructure),
                   # action_to_check_outcome=asrt.is_instance(ActionToCheckOutcome))
                   )


def is_xpass() -> asrt.ValueAssertion[FullResult]:
    return matches(status=asrt.is_(FullResultStatus.XPASS),
                   failure_info=asrt.is_none,
                   sds=asrt.is_instance(SandboxDirectoryStructure),
                   # action_to_check_outcome=asrt.is_instance(ActionToCheckOutcome))
                   )


def is_skipped() -> asrt.ValueAssertion[FullResult]:
    return matches(status=asrt.is_(FullResultStatus.SKIPPED),
                   failure_info=asrt.is_none,
                   sds=asrt.is_none,
                   action_to_check_outcome=asrt.is_none)


def is_failure(status: FullResultStatus,
               failure_info: asrt.ValueAssertion[Optional[FailureInfo]] = asrt.is_instance(FailureInfo),
               sds: asrt.ValueAssertion[Optional[SandboxDirectoryStructure]] = asrt.anything_goes(),
               action_to_check_outcome: asrt.ValueAssertion[Optional[ActionToCheckOutcome]] = asrt.anything_goes(),
               ) -> asrt.ValueAssertion[FullResult]:
    return matches(status=asrt.is_(status),
                   sds=sds,
                   action_to_check_outcome=action_to_check_outcome,
                   failure_info=failure_info)


def matches(
        status: asrt.ValueAssertion[FullResultStatus] = asrt.anything_goes(),
        sds: asrt.ValueAssertion[Optional[SandboxDirectoryStructure]] = asrt.anything_goes(),
        action_to_check_outcome: asrt.ValueAssertion[Optional[ActionToCheckOutcome]] = asrt.anything_goes(),
        failure_info: asrt.ValueAssertion[Optional[FailureInfo]] = asrt.anything_goes(),
) -> asrt.ValueAssertion[FullResult]:
    return asrt.and_([
        asrt.sub_component('status',
                           FullResult.status.fget,
                           status),
        asrt.sub_component('sds',
                           FullResult.sds.fget,
                           sds),
        asrt.sub_component('action_to_check_outcome',
                           FullResult.action_to_check_outcome.fget,
                           action_to_check_outcome),
        asrt.sub_component('failure_info',
                           FullResult.failure_info.fget,
                           failure_info),
    ])
