import unittest

from exactly_lib.util.interval import int_interval as sut
from exactly_lib.util.interval.int_interval import IntInterval
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.interval.test_resources.interval_assertion import matches_empty, \
    matches_point, matches_lower_limit, matches_upper_limit, matches_finite, matches_unlimited


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestEmpty(),
        TestUnlimited(),
        TestPoint(),
        TestLowerLimit(),
        TestUpperLimit(),
        TestFinite(),
    ])


class TestEmpty(unittest.TestCase):
    def runTest(self):
        _check_single(
            self,
            sut.Empty(),
            matches_empty(),
        )


class TestUnlimited(unittest.TestCase):
    def runTest(self):
        _check_single(
            self,
            sut.unlimited(),
            matches_unlimited(),
        )


class TestPoint(unittest.TestCase):
    def runTest(self):
        _check_single(
            self,
            sut.point(7),
            matches_point(7),
        )


class TestLowerLimit(unittest.TestCase):
    def runTest(self):
        _check_single(
            self,
            sut.lower_limit(-5),
            matches_lower_limit(-5),
        )


class TestUpperLimit(unittest.TestCase):
    def runTest(self):
        _check_single(
            self,
            sut.upper_limit(-5),
            matches_upper_limit(-5),
        )


class TestFinite(unittest.TestCase):
    def runTest(self):
        _check_single(
            self,
            sut.finite(0, 13),
            matches_finite(0, 13),
        )


def _check_single(put: unittest.TestCase,
                  actual: IntInterval,
                  expectation: ValueAssertion[IntInterval]):
    expectation.apply_with_message(put, actual, 'positive value')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
