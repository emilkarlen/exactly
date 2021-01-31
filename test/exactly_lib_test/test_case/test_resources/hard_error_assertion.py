import unittest
from typing import Any, Callable, Generic

from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import AssertionBase, MessageBuilder, T


class RaisesHardError(Generic[T], AssertionBase[T]):
    def __init__(self, method_that_should_raise: Callable[[T], Any]):
        self._method_that_should_raise = method_that_should_raise

    def _apply(self,
               put: unittest.TestCase,
               value: T,
               message_builder: MessageBuilder):
        with put.assertRaises(HardErrorException) as cx:
            self._method_that_should_raise(value)
        asrt_text_doc.is_any_text().apply(
            put,
            cx.exception.error,
            message_builder.for_sub_component('error message'),
        )


class RaisesHardErrorAsLastAction(Generic[T], AssertionBase[T]):
    """"Checks that :class:`HardErrorException` is raised,
    and stops further assertions by raising :class:`asrt.StopAssertion`"""

    def __init__(self, method_that_should_raise: Callable[[T], Any]):
        self._method_that_should_raise = method_that_should_raise

    def _apply(self,
               put: unittest.TestCase,
               value: T,
               message_builder: MessageBuilder):
        try:
            self._method_that_should_raise(value)
            put.fail('HardErrorException not raised')
        except HardErrorException as ex:
            asrt_text_doc.is_any_text().apply(
                put,
                ex.error,
                message_builder.for_sub_component('error message'),
            )
            raise asrt.StopAssertion()
