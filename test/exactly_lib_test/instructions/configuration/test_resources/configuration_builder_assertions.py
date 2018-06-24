from typing import Optional

from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib.test_case.test_case_status import ExecutionMode
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def has(timeout: asrt.ValueAssertion[Optional[int]] = asrt.anything_goes(),
        test_case_status: asrt.ValueAssertion[ExecutionMode] = asrt.anything_goes(),
        ) -> asrt.ValueAssertion[ConfigurationBuilder]:
    return asrt.and_([
        asrt.sub_component('timeout',
                           ConfigurationBuilder.timeout_in_seconds.fget,
                           timeout),
        asrt.sub_component('test-case-status',
                           ConfigurationBuilder.execution_mode.fget,
                           test_case_status),
    ])
