"""
ValueAssertion:s on FullResult
"""
from exactly_lib.execution.result import FullResult, FullResultStatus
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt

is_pass = asrt.OnTransformed(FullResult.status.fget,
                             asrt.Equals(FullResultStatus.PASS,
                                     'Status is expected to be PASS'))
