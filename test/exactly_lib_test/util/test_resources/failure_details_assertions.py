import unittest
from typing import Optional, Type

from exactly_lib.util import file_printer
from exactly_lib.util.failure_details import FailureDetails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder, ValueAssertionBase
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def is_failure_message_of(msg: str) -> ValueAssertion[FailureDetails]:
    return is_failure_message_matching(asrt.equals(msg))


def is_any_failure_message() -> ValueAssertion[FailureDetails]:
    return _ExpectedFailureDetails(asrt.is_not_none_and_instance_with(str, asrt.anything_goes()),
                                   None)


def is_failure_message_matching(expected: ValueAssertion[str]) -> ValueAssertion[FailureDetails]:
    return _ExpectedFailureDetails(asrt.is_not_none_and_instance_with(str, expected),
                                   None)


def is_exception(exception_class: Type[Exception]) -> ValueAssertion[FailureDetails]:
    return _ExpectedFailureDetails(None, exception_class)


class _ExpectedFailureDetails(ValueAssertionBase[FailureDetails]):
    def __init__(self,
                 error_message_or_none: Optional[ValueAssertion[str]],
                 exception_class_or_none: Optional[type]):
        if error_message_or_none is not None:
            if isinstance(error_message_or_none, str):
                raise TypeError(error_message_or_none)
        self._error_message_or_none = error_message_or_none
        self._exception_class_or_none = exception_class_or_none

    def _apply(self,
               put: unittest.TestCase,
               value: FailureDetails,
               message_builder: MessageBuilder):
        self.assertions(put, value, message_builder.apply(''))

    @property
    def error_message_or_none(self) -> ValueAssertion:
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
            err_msg = message_builder.for_sub_component('failure message')
            put.assertIsNotNone(actual.failure_message,
                                err_msg)
            actual_failure_message = file_printer.print_to_string(actual.failure_message)
            self.error_message_or_none.apply(put,
                                             actual_failure_message,
                                             err_msg)
        else:
            put.assertIsInstance(actual.exception,
                                 self.exception_class_or_none,
                                 message_builder.for_sub_component('exception class'))


class _EqualsFailureDetails(ValueAssertionBase[FailureDetails]):
    def __init__(self, expected: FailureDetails):
        self._expected = expected

    def _apply(self,
               put: unittest.TestCase,
               actual: FailureDetails,
               message_builder: MessageBuilder):
        put.assertEqual(self._expected.failure_message is not None,
                        actual.failure_message is not None,
                        message_builder.apply('has message'))

        put.assertEqual(self._expected.is_only_failure_message is not None,
                        actual.is_only_failure_message is not None,
                        message_builder.apply('is_only_failure_message'))

        put.assertEqual(self._expected.has_exception is not None,
                        actual.has_exception is not None,
                        message_builder.apply('has exception'))

        if self._expected.failure_message is not None:
            expected_msg = file_printer.print_to_string(self._expected.failure_message)
            actual_msg = file_printer.print_to_string(actual.failure_message)

            put.assertEqual(expected_msg,
                            actual_msg,
                            message_builder.apply('failure_message'))

        if self._expected.exception is not None:
            put.assertEqual(self._expected.exception,
                            actual.exception,
                            message_builder.apply('exception'))


def equals_failure_details(expected: FailureDetails) -> ValueAssertion[FailureDetails]:
    return _EqualsFailureDetails(expected)


def assert_equal_failure_details(put: unittest.TestCase,
                                 expected: FailureDetails,
                                 actual: FailureDetails):
    equals_failure_details(expected).apply_without_message(put, actual)
