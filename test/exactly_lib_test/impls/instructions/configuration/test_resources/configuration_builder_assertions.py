from typing import Optional

from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib.test_case.test_case_status import TestCaseStatus
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def has(timeout: ValueAssertion[Optional[int]] = asrt.anything_goes(),
        test_case_status: ValueAssertion[TestCaseStatus] = asrt.anything_goes(),
        ) -> ValueAssertion[ConfigurationBuilder]:
    return asrt.and_([
        asrt.sub_component('timeout',
                           ConfigurationBuilder.timeout_in_seconds.fget,
                           timeout),
        asrt.sub_component('test-case-status',
                           ConfigurationBuilder.test_case_status.fget,
                           test_case_status),
    ])