"""
ValueAssertion:s on FullResult
"""
from exactly_lib.execution.result import FullResult, FullResultStatus
from exactly_lib_test.test_resources.value_assertions import value_assertion as va

is_pass = va.OnTransformed(FullResult.status.fget,
                           va.Equals(FullResultStatus.PASS,
                                     'Status is expected to be PASS'))
