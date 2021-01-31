import unittest
from typing import TypeVar, Callable

from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


class TestException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


def test_case_with_failure_exception_set_to_test_exception() -> unittest.TestCase:
    put = unittest.TestCase()
    put.failureException = TestException
    return put


T = TypeVar('T')


def assert_that_assertion_fails(assertion: Assertion[T],
                                actual: T):
    put = test_case_with_failure_exception_set_to_test_exception()
    with put.assertRaises(TestException):
        assertion.apply_without_message(put, actual)


def assert_fails(assertion: Callable[[unittest.TestCase], None]):
    put = test_case_with_failure_exception_set_to_test_exception()
    with put.assertRaises(TestException):
        assertion(put)
