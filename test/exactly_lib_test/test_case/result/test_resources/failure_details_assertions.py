import unittest
from typing import Optional, Type

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case.result.failure_details import FailureDetails
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder, AssertionBase


def is_failure_message_of(msg: str) -> Assertion[FailureDetails]:
    return is_failure_message_matching(asrt.equals(msg))


def is_any_failure_message() -> Assertion[FailureDetails]:
    return _ExpectedFailureDetailsTd(asrt_text_doc.is_any_text(),
                                     asrt.anything_goes())


def is_failure_message_matching(expected: Assertion[str]) -> Assertion[FailureDetails]:
    return _ExpectedFailureDetails(asrt.is_not_none_and_instance_with(str, expected),
                                   asrt.anything_goes())


def is_failure_message_matching__td(expected: Assertion[TextRenderer]) -> Assertion[FailureDetails]:
    return _ExpectedFailureDetailsTd(expected,
                                     asrt.anything_goes())


def is_exception_of_type(exception_class: Type[Exception]) -> Assertion[FailureDetails]:
    return matches_exception(asrt.is_not_none_and_instance_with(exception_class,
                                                                asrt.anything_goes()))


def matches_exception(exception: Assertion[Optional[Exception]]) -> Assertion[FailureDetails]:
    return _ExpectedFailureDetailsTd(None, exception)


class _ExpectedFailureDetails(AssertionBase[FailureDetails]):
    def __init__(self,
                 error_message_or_none: Optional[Assertion[str]],
                 exception_or_none: Assertion[Optional[Exception]]):
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
            message_comp_builder = message_builder.for_sub_component('failure message')
            put.assertIsNotNone(value.failure_message,
                                message_comp_builder)

            asrt_text_doc.is_string_for_test(self._error_message_or_none).apply(
                put,
                value.failure_message,
                message_comp_builder.for_sub_component('text-doc')
            )

        self._exception_or_none.apply(put,
                                      value.exception,
                                      message_builder.for_sub_component('exception'))


class _ExpectedFailureDetailsTd(AssertionBase[FailureDetails]):
    def __init__(self,
                 error_message_or_none: Optional[Assertion[TextRenderer]],
                 exception_or_none: Assertion[Optional[Exception]]):
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
            message_comp_builder = message_builder.for_sub_component('failure message')
            put.assertIsNotNone(value.failure_message,
                                message_comp_builder)

            self._error_message_or_none.apply(
                put,
                value.failure_message,
                message_comp_builder.for_sub_component('text-doc')
            )

        self._exception_or_none.apply(put,
                                      value.exception,
                                      message_builder.for_sub_component('exception'))
