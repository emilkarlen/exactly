import unittest
from typing import Optional, Type

from exactly_lib.test_case.result.failure_details import FailureDetails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder, ValueAssertionBase
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.test_resources import file_printable_assertions as asrt_file_printable


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
        self._error_message_or_none = error_message_or_none
        self._exception_class_or_none = exception_class_or_none
        if self.error_message_or_none is None and self.exception_class_or_none is None:
            raise ValueError('At least one assertion must be given')

    def _apply(self,
               put: unittest.TestCase,
               value: Optional[FailureDetails],
               message_builder: MessageBuilder):
        put.assertIsNotNone(value,
                            message_builder.apply('must not be none'))
        put.assertIsInstance(value,
                             FailureDetails,
                             message_builder.apply('type of object'))

        if self.error_message_or_none is not None:
            err_msg = message_builder.for_sub_component('failure message')
            put.assertIsNotNone(value.failure_message,
                                err_msg)
            assertion = asrt_file_printable.matches(self.error_message_or_none)
            assertion.apply(put, value.failure_message, err_msg)

        if self.exception_class_or_none is None:
            put.assertIsNone(value.exception,
                             message_builder.for_sub_component('exception'))
        else:
            put.assertIsInstance(value.exception,
                                 self.exception_class_or_none,
                                 message_builder.for_sub_component('exception'))

    @property
    def error_message_or_none(self) -> Optional[ValueAssertion[str]]:
        return self._error_message_or_none

    @property
    def exception_class_or_none(self):
        return self._exception_class_or_none


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
            failure_message_assertion = asrt_file_printable.equals(self._expected.failure_message)
            failure_message_assertion.apply(put,
                                            actual.failure_message,
                                            message_builder.for_sub_component(
                                                'failure_message'))

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
