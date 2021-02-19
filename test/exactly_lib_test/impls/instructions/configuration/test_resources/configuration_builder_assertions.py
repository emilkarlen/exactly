from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib.test_case.test_case_status import TestCaseStatus
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def matches(status: Assertion[TestCaseStatus] = asrt.anything_goes(),
            ) -> Assertion[ConfigurationBuilder]:
    return asrt.and_([
        asrt.sub_component('test-case-status',
                           ConfigurationBuilder.test_case_status.fget,
                           status),
    ])
