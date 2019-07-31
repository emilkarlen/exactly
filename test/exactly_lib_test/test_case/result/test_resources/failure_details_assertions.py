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
                                   asrt.anything_goes())


def is_failure_message_matching(expected: ValueAssertion[str]) -> ValueAssertion[FailureDetails]:
    return _ExpectedFailureDetails(asrt.is_not_none_and_instance_with(str, expected),
                                   asrt.anything_goes())


def is_exception_of_type(exception_class: Type[Exception]) -> ValueAssertion[FailureDetails]:
    return matches_exception(asrt.is_not_none_and_instance_with(exception_class,
                                                                asrt.anything_goes()))


def matches_exception(exception: ValueAssertion[Optional[Exception]]) -> ValueAssertion[FailureDetails]:
    return _ExpectedFailureDetails(None, exception)


class _ExpectedFailureDetails(ValueAssertionBase[FailureDetails]):
    def __init__(self,
                 error_message_or_none: Optional[ValueAssertion[str]],
                 exception_or_none: ValueAssertion[Optional[Exception]]):
        self._error_message_or_none = error_message_or_none
        self._exception_or_none = exception_or_none
        if self._error_message_or_none is None and self._exception_or_none is None:
            raise ValueError('At least one assertion must be given')

    def _apply(self,
               put: unittest.TestCase,
               value: FailureDetails,
               message_builder: MessageBuilder):
        put.assertIsNotNone(value,
                            message_builder.apply('must not be none'))
        put.assertIsInstance(value,
                             FailureDetails,
                             message_builder.apply('type of object'))

        if self._error_message_or_none is not None:
            err_msg = message_builder.for_sub_component('failure message')
            put.assertIsNotNone(value.failure_message,
                                err_msg)
            assertion = asrt_file_printable.matches(self._error_message_or_none)
            assertion.apply(put, value.failure_message, err_msg)

        self._exception_or_none.apply(put,
                                      value.exception,
                                      message_builder.for_sub_component('exception'))
