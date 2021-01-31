import unittest

from exactly_lib.util.interval import int_interval
from exactly_lib.util.interval.int_interval import IntInterval
from exactly_lib.util.interval.w_inversion import intervals as sut
from exactly_lib.util.interval.w_inversion.interval import IntIntervalWInversion
from exactly_lib.util.interval.w_inversion.intervals import Empty, \
    Unlimited
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.util.interval.test_resources.interval_assertion import matches_empty, \
    matches_point, matches_lower_limit, matches_upper_limit, matches_finite, matches_unlimited, PosNeg


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestEmpty(),
        TestUnlimited(),
        TestPoint(),
        TestLowerLimit(),
        TestUpperLimit(),
        TestFinite(),
        TestWithCustomInversion(),
    ])


class Case:
    def __init__(self,
                 a: IntIntervalWInversion,
                 b: IntIntervalWInversion,
                 union: PosNeg[IntIntervalWInversion],
                 intersection: PosNeg,
                 ):
        self.a = a
        self.b = b
        self.union = union
        self.intersection = intersection


empty = Empty()
unlimited = Unlimited()


class TestEmpty(unittest.TestCase):
    def runTest(self):
        _check_single(
            self,
            sut.Empty(),
            matches_empty(),
            matches_unlimited(),
        )


class TestUnlimited(unittest.TestCase):
    def runTest(self):
        _check_single(
            self,
            sut.Unlimited(),
            matches_unlimited(),
            matches_empty(),
        )


class TestPoint(unittest.TestCase):
    def runTest(self):
        _check_single(
            self,
            sut.point(7),
            matches_point(7),
            matches_unlimited(),
        )


class TestLowerLimit(unittest.TestCase):
    def runTest(self):
        _check_single(
            self,
            sut.LowerLimit(-5),
            matches_lower_limit(-5),
            matches_upper_limit(-5 - 1),
        )


class TestUpperLimit(unittest.TestCase):
    def runTest(self):
        _check_single(
            self,
            sut.UpperLimit(-5),
            matches_upper_limit(-5),
            matches_lower_limit(-5 + 1),
        )


class TestFinite(unittest.TestCase):
    def runTest(self):
        _check_single(
            self,
            sut.Finite(0, 13),
            matches_finite(0, 13),
            matches_unlimited(),
        )


class TestWithCustomInversion(unittest.TestCase):
    def runTest(self):
        _check_single(
            self,
            sut.WithCustomInversion(
                int_interval.point(5),
                int_interval.upper_limit(12)
            ),
            matches_point(5),
            matches_upper_limit(12),
        )


def _check_single(put: unittest.TestCase,
                  actual: IntIntervalWInversion,
                  pos: Assertion[IntInterval],
                  neg: Assertion[IntInterval]):
    pos.apply_with_message(put, actual, 'positive value')
    neg.apply_with_message(put, actual.inversion, 'inversion')
    pos.apply_with_message(put, actual.inversion.inversion, 'double inversion')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
