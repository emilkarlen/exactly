import unittest
from typing import Optional

from exactly_lib.execution.impl.result import Failure
from exactly_lib.execution.partial_execution.result import PartialExeResultStatus
from exactly_lib.util.failure_details import FailureDetails
from exactly_lib.util.line_source import SourceLocationPath
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder


class _ExpectedFailure(asrt.ValueAssertion[Optional[Failure]]):
    def __init__(self,
                 status: PartialExeResultStatus,
                 line: asrt.ValueAssertion[SourceLocationPath],
                 failure_details: asrt.ValueAssertion[FailureDetails]):
        self._status = status
        self._line = line
        self._failure_details = failure_details

    def apply(self,
              put: unittest.TestCase,
              value: Optional[Failure],
              message_builder: MessageBuilder = MessageBuilder()):
        self._assertions(put, value)

    def _assertions(self,
                    unittest_case: unittest.TestCase,
                    return_value: Failure):
        if self._status is PartialExeResultStatus.PASS:
            unittest_case.assertIsNone(return_value,
                                       'Return value must be None (representing success)')
        else:
            unittest_case.assertIsNotNone(return_value,
                                          'Return value must not be None (representing failure)')
            unittest_case.assertEqual(self._status,
                                      return_value.status,
                                      'Status')
            self._line.apply_with_message(unittest_case,
                                          return_value.source_location,
                                          'source location path')
            unittest_case.assertIsNotNone(return_value.failure_details,
                                          'failure_details must be present')
            self._failure_details.apply_with_message(unittest_case,
                                                     return_value.failure_details,
                                                     'failure_details')


def is_not_present() -> asrt.ValueAssertion[Optional[Failure]]:
    return asrt.is_none


def is_present_with(status: PartialExeResultStatus,
                    line: asrt.ValueAssertion[SourceLocationPath],
                    failure_details: asrt.ValueAssertion[FailureDetails]) -> asrt.ValueAssertion[Optional[Failure]]:
    if status is PartialExeResultStatus.PASS:
        raise ValueError('{} is not a failure', status)
    return asrt.is_not_none_and_instance_with(Failure,
                                              _ExpectedFailure(status,
                                                               line,
                                                               failure_details))
