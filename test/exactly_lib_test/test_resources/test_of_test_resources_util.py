import unittest

from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class TestException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


def test_case_with_failure_exception_set_to_test_exception() -> unittest.TestCase:
    put = unittest.TestCase()
    put.failureException = TestException
    return put


def assert_that_assertion_fails(assertion: asrt.ValueAssertion,
                                actual):
    put = test_case_with_failure_exception_set_to_test_exception()
    with put.assertRaises(TestException):
        assertion.apply_without_message(put, actual)
