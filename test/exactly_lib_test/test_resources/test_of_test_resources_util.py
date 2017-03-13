import unittest


class TestException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


def test_case_with_failure_exception_set_to_test_exception() -> unittest.TestCase:
    put = unittest.TestCase()
    put.failureException = TestException
    return put
