import unittest
from typing import Optional, Type

from exactly_lib.util.failure_details import FailureDetails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder


def is_failure_message_of(msg: str) -> asrt.ValueAssertion[FailureDetails]:
    return is_failure_message_matching(asrt.equals(msg))


def is_any_failure_message() -> asrt.ValueAssertion[FailureDetails]:
    return _ExpectedFailureDetails(asrt.is_not_none_and_instance_with(str, asrt.anything_goes()),
                                   None)


def is_failure_message_matching(expected: asrt.ValueAssertion[str]) -> asrt.ValueAssertion[FailureDetails]:
    return _ExpectedFailureDetails(asrt.is_not_none_and_instance_with(str, expected),
                                   None)


def is_exception(exception_class: Type[Exception]) -> asrt.ValueAssertion[FailureDetails]:
    return _ExpectedFailureDetails(None, exception_class)


class _ExpectedFailureDetails(asrt.ValueAssertion[FailureDetails]):
    def __init__(self,
                 error_message_or_none: Optional[asrt.ValueAssertion[str]],
                 exception_class_or_none: Optional[Type[Exception]]):
        if error_message_or_none is not None:
            if isinstance(error_message_or_none, str):
                raise TypeError(error_message_or_none)
        self._error_message_or_none = error_message_or_none
        self._exception_class_or_none = exception_class_or_none

    def apply(self,
              put: unittest.TestCase,
              value: FailureDetails,
              message_builder: MessageBuilder = MessageBuilder()):
        self.assertions(put, value, message_builder.apply(''))

    @property
    def error_message_or_none(self) -> asrt.ValueAssertion:
        return self._error_message_or_none

    @property
    def exception_class_or_none(self):
        return self._exception_class_or_none

    def assertions(self,
                   put: unittest.TestCase,
                   actual: FailureDetails,
                   message_header: str = None):
        message_builder = asrt.new_message_builder(message_header)
        if self.error_message_or_none is None and self.exception_class_or_none is None:
            put.assertIsNone(actual,
                             message_header)
        elif self.error_message_or_none is not None:
            self.error_message_or_none.apply_with_message(put,
                                                          actual.failure_message,
                                                          message_builder.for_sub_component('failure message'))
        else:
            put.assertIsInstance(actual.exception,
                                 self.exception_class_or_none,
                                 message_builder.for_sub_component('exception class'))
