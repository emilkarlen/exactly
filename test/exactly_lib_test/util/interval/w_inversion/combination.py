import unittest
from typing import Sequence

from exactly_lib.util.interval.w_inversion import combinations as sut
from exactly_lib.util.interval.w_inversion.interval import IntIntervalWInversion
from exactly_lib.util.interval.w_inversion.intervals import UpperLimit, LowerLimit, Finite, point, Empty, \
    Unlimited
from exactly_lib_test.util.interval.test_resources.interval_assertion import equals_interval, PosNeg


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestCombination)


class Case:
    def __init__(self,
                 a: IntIntervalWInversion,
                 b: IntIntervalWInversion,
                 union: PosNeg[IntIntervalWInversion],
                 intersection: PosNeg[IntIntervalWInversion],
                 ):
        self.a = a
        self.b = b
        self.union = union
        self.intersection = intersection


empty = Empty()
unlimited = Unlimited()


class TestCombination(unittest.TestCase):
    def test_point_empty(self):
        _check_permutations(self, [
            Case(
                point(7), empty,
                union=PosNeg(point(7), unlimited),
                intersection=PosNeg(empty, unlimited),
            ),
        ])

    def test_point_unlimited(self):
        _check_permutations(self, [
            Case(
                point(7), unlimited,
                union=PosNeg(unlimited, empty),  # negering: kan få unlimited??
                intersection=PosNeg(point(7), unlimited),
            ),
        ])

    def test_point_point(self):
        _check_permutations(self, [
            Case(
                point(7), point(7),
                union=PosNeg(point(7), unlimited),
                intersection=PosNeg(point(7), unlimited),
            ),
            Case(
                point(3), point(7),
                union=PosNeg(Finite(3, 7), unlimited),
                intersection=PosNeg(empty, unlimited),
            ),
        ])

    def test_point_lower(self):
        _check_permutations(self, [
            Case(
                point(3), LowerLimit(5),
                union=PosNeg(LowerLimit(3), UpperLimit(3 - 1)),
                intersection=PosNeg(empty, unlimited),
            ),
            Case(
                point(4), LowerLimit(5),
                union=PosNeg(LowerLimit(4), UpperLimit(4 - 1)),
                intersection=PosNeg(empty, unlimited),
            ),
            Case(
                point(5), LowerLimit(5),
                union=PosNeg(LowerLimit(5), UpperLimit(5 - 1)),
                intersection=PosNeg(point(5), unlimited),
            ),
            Case(
                point(6), LowerLimit(5),
                union=PosNeg(LowerLimit(5), UpperLimit(5 - 1)),
                intersection=PosNeg(point(6), unlimited),
            ),
            Case(
                point(7), LowerLimit(5),
                union=PosNeg(LowerLimit(5), UpperLimit(5 - 1)),
                intersection=PosNeg(point(7), unlimited),
            ),
        ])

    def test_point_upper(self):
        _check_permutations(self, [
            Case(
                point(-3), UpperLimit(0),
                union=PosNeg(UpperLimit(0), LowerLimit(0 + 1)),
                intersection=PosNeg(point(-3), unlimited),
            ),
            Case(
                point(6), UpperLimit(9),
                union=PosNeg(UpperLimit(9), LowerLimit(9 + 1)),
                intersection=PosNeg(point(6), unlimited),
            ),
            Case(
                point(7), UpperLimit(9),
                union=PosNeg(UpperLimit(9), LowerLimit(9 + 1)),
                intersection=PosNeg(point(7), unlimited),
            ),
            Case(
                point(8), UpperLimit(9),
                union=PosNeg(UpperLimit(9), LowerLimit(9 + 1)),
                intersection=PosNeg(point(8), unlimited),
            ),
            Case(
                point(9), UpperLimit(9),
                union=PosNeg(UpperLimit(9), LowerLimit(9 + 1)),
                intersection=PosNeg(point(9), unlimited),
            ),
            Case(
                point(10), UpperLimit(9),
                union=PosNeg(UpperLimit(10), LowerLimit(10 + 1)),
                intersection=PosNeg(empty, unlimited),
            ),
            Case(
                point(11), UpperLimit(9),
                union=PosNeg(UpperLimit(11), LowerLimit(11 + 1)),
                intersection=PosNeg(empty, unlimited),
            ),
        ])

    def test_point_finite(self):
        _check_permutations(self, [
            Case(
                point(3), Finite(5, 9),
                union=PosNeg(Finite(3, 9), unlimited),
                intersection=PosNeg(empty, unlimited),
            ),
            Case(
                point(4), Finite(5, 9),
                union=PosNeg(Finite(4, 9), unlimited),
                intersection=PosNeg(empty, unlimited),
            ),
            Case(
                point(5), Finite(5, 9),
                union=PosNeg(Finite(5, 9), unlimited),
                intersection=PosNeg(point(5), unlimited),
            ),
            Case(
                point(6), Finite(5, 9),
                union=PosNeg(Finite(5, 9), unlimited),
                intersection=PosNeg(point(6), unlimited),
            ),
            Case(
                point(7), Finite(5, 9),
                union=PosNeg(Finite(5, 9), unlimited),
                intersection=PosNeg(point(7), unlimited),
            ),
            Case(
                point(8), Finite(5, 9),
                union=PosNeg(Finite(5, 9), unlimited),
                intersection=PosNeg(point(8), unlimited),
            ),
            Case(
                point(9), Finite(5, 9),
                union=PosNeg(Finite(5, 9), unlimited),
                intersection=PosNeg(point(9), unlimited),
            ),
            Case(
                point(10), Finite(5, 9),
                union=PosNeg(Finite(5, 10), unlimited),
                intersection=PosNeg(empty, unlimited),
            ),
            Case(
                point(11), Finite(5, 9),
                union=PosNeg(Finite(5, 11), unlimited),
                intersection=PosNeg(empty, unlimited),
            ),
        ])

    def test_lower_empty(self):
        _check_permutations(self, [
            Case(
                LowerLimit(7), empty,
                union=PosNeg(LowerLimit(7), UpperLimit(7 - 1)),
                intersection=PosNeg(empty, unlimited),
            ),
        ])

    def test_lower_unlimited(self):
        _check_permutations(self, [
            Case(
                LowerLimit(7), unlimited,
                union=PosNeg(unlimited, empty),
                intersection=PosNeg(LowerLimit(7), UpperLimit(7 - 1)),
            ),
        ])

    def test_lower_lower(self):
        _check_permutations(self, [
            Case(
                LowerLimit(3), LowerLimit(5),
                union=PosNeg(LowerLimit(3), UpperLimit(3 - 1)),
                intersection=PosNeg(LowerLimit(5), UpperLimit(5 - 1)),
            ),
            Case(
                LowerLimit(4), LowerLimit(5),
                union=PosNeg(LowerLimit(4), UpperLimit(4 - 1)),
                intersection=PosNeg(LowerLimit(5), UpperLimit(5 - 1)),
            ),
            Case(
                LowerLimit(5), LowerLimit(5),
                union=PosNeg(LowerLimit(5), UpperLimit(5 - 1)),
                intersection=PosNeg(LowerLimit(5), UpperLimit(5 - 1)),
            ),
            Case(
                LowerLimit(6), LowerLimit(5),
                union=PosNeg(LowerLimit(5), UpperLimit(5 - 1)),
                intersection=PosNeg(LowerLimit(6), UpperLimit(6 - 1)),
            ),
            Case(
                LowerLimit(7), LowerLimit(5),
                union=PosNeg(LowerLimit(5), UpperLimit(5 - 1)),
                intersection=PosNeg(LowerLimit(7), UpperLimit(7 - 1)),
            ),
        ])

    def test_lower_upper(self):
        _check_permutations(self, [
            Case(
                LowerLimit(3), UpperLimit(5),
                union=PosNeg(unlimited, empty),
                intersection=PosNeg(Finite(3, 5), unlimited),
            ),
            Case(
                LowerLimit(4), UpperLimit(5),
                union=PosNeg(unlimited, empty),
                intersection=PosNeg(Finite(4, 5), unlimited),
            ),
            Case(
                LowerLimit(5), UpperLimit(5),
                union=PosNeg(unlimited, empty),
                intersection=PosNeg(point(5), unlimited),
            ),
            Case(
                LowerLimit(6), UpperLimit(5),
                union=PosNeg(unlimited, empty),
                intersection=PosNeg(empty, unlimited),
            ),
            Case(
                LowerLimit(7), UpperLimit(5),
                union=PosNeg(unlimited, empty),
                intersection=PosNeg(empty, unlimited),
            ),
        ])

    def test_lower_finite(self):
        _check_permutations(self, [
            Case(
                LowerLimit(3), Finite(5, 9),
                union=PosNeg(LowerLimit(3), UpperLimit(3 - 1)),
                intersection=PosNeg(Finite(5, 9), unlimited),
            ),
            Case(
                LowerLimit(4), Finite(5, 9),
                union=PosNeg(LowerLimit(4), UpperLimit(4 - 1)),
                intersection=PosNeg(Finite(5, 9), unlimited),
            ),
            Case(
                LowerLimit(5), Finite(5, 9),
                union=PosNeg(LowerLimit(5), UpperLimit(5 - 1)),
                intersection=PosNeg(Finite(5, 9), unlimited),
            ),
            Case(
                LowerLimit(6), Finite(5, 9),
                union=PosNeg(LowerLimit(5), UpperLimit(5 - 1)),
                intersection=PosNeg(Finite(6, 9), unlimited),
            ),
            Case(
                LowerLimit(7), Finite(5, 9),
                union=PosNeg(LowerLimit(5), UpperLimit(5 - 1)),
                intersection=PosNeg(Finite(7, 9), unlimited),
            ),
            Case(
                LowerLimit(8), Finite(5, 9),
                union=PosNeg(LowerLimit(5), UpperLimit(5 - 1)),
                intersection=PosNeg(Finite(8, 9), unlimited),
            ),
            Case(
                LowerLimit(9), Finite(5, 9),
                union=PosNeg(LowerLimit(5), UpperLimit(5 - 1)),
                intersection=PosNeg(point(9), unlimited),
            ),
            Case(
                LowerLimit(10), Finite(5, 9),
                union=PosNeg(LowerLimit(5), UpperLimit(5 - 1)),
                intersection=PosNeg(empty, unlimited),
            ),
            Case(
                LowerLimit(11), Finite(5, 9),
                union=PosNeg(LowerLimit(5), UpperLimit(5 - 1)),
                intersection=PosNeg(empty, unlimited),
            ),
        ])

    def test_upper_empty(self):
        _check_permutations(self, [
            Case(
                UpperLimit(7), empty,
                union=PosNeg(UpperLimit(7), LowerLimit(7 + 1)),
                intersection=PosNeg(empty, unlimited),
            ),
        ])

    def test_upper_unlimited(self):
        _check_permutations(self, [
            Case(
                UpperLimit(7), unlimited,
                union=PosNeg(unlimited, empty),
                intersection=PosNeg(UpperLimit(7), LowerLimit(7 + 1)),
            ),
        ])

    def test_upper_upper(self):
        _check_permutations(self, [
            Case(
                UpperLimit(3), UpperLimit(5),
                union=PosNeg(UpperLimit(5), LowerLimit(5 + 1)),
                intersection=PosNeg(UpperLimit(3), LowerLimit(3 + 1)),
            ),
            Case(
                UpperLimit(4), UpperLimit(5),
                union=PosNeg(UpperLimit(5), LowerLimit(5 + 1)),
                intersection=PosNeg(UpperLimit(4), LowerLimit(4 + 1)),
            ),
            Case(
                UpperLimit(5), UpperLimit(5),
                union=PosNeg(UpperLimit(5), LowerLimit(5 + 1)),
                intersection=PosNeg(UpperLimit(5), LowerLimit(5 + 1)),
            ),
            Case(
                UpperLimit(6), UpperLimit(5),
                union=PosNeg(UpperLimit(6), LowerLimit(6 + 1)),
                intersection=PosNeg(UpperLimit(5), LowerLimit(5 + 1)),
            ),
            Case(
                UpperLimit(7), UpperLimit(5),
                union=PosNeg(UpperLimit(7), LowerLimit(7 + 1)),
                intersection=PosNeg(UpperLimit(5), LowerLimit(5 + 1)),
            ),
        ])

    def test_upper_finite(self):
        _check_permutations(self, [
            Case(
                UpperLimit(3), Finite(5, 9),
                union=PosNeg(UpperLimit(9), LowerLimit(9 + 1)),
                intersection=PosNeg(empty, unlimited),
            ),
            Case(
                UpperLimit(4), Finite(5, 9),
                union=PosNeg(UpperLimit(9), LowerLimit(9 + 1)),
                intersection=PosNeg(empty, unlimited),
            ),
            Case(
                UpperLimit(5), Finite(5, 9),
                union=PosNeg(UpperLimit(9), LowerLimit(9 + 1)),
                intersection=PosNeg(point(5), unlimited),
            ),
            Case(
                UpperLimit(6), Finite(5, 9),
                union=PosNeg(UpperLimit(9), LowerLimit(9 + 1)),
                intersection=PosNeg(Finite(5, 6), unlimited),
            ),
            Case(
                UpperLimit(7), Finite(5, 9),
                union=PosNeg(UpperLimit(9), LowerLimit(9 + 1)),
                intersection=PosNeg(Finite(5, 7), unlimited),
            ),
            Case(
                UpperLimit(8), Finite(5, 9),
                union=PosNeg(UpperLimit(9), LowerLimit(9 + 1)),
                intersection=PosNeg(Finite(5, 8), unlimited),
            ),
            Case(
                UpperLimit(9), Finite(5, 9),
                union=PosNeg(UpperLimit(9), LowerLimit(9 + 1)),
                intersection=PosNeg(Finite(5, 9), unlimited),
            ),
            Case(
                UpperLimit(10), Finite(5, 9),
                union=PosNeg(UpperLimit(10), LowerLimit(10 + 1)),
                intersection=PosNeg(Finite(5, 9), unlimited),
            ),
            Case(
                UpperLimit(11), Finite(5, 9),
                union=PosNeg(UpperLimit(11), LowerLimit(11 + 1)),
                intersection=PosNeg(Finite(5, 9), unlimited),
            ),
        ])

    def test_finite_empty(self):
        _check_permutations(self, [
            Case(
                Finite(3, 7), empty,
                union=PosNeg(Finite(3, 7), unlimited),
                intersection=PosNeg(empty, unlimited),
            ),
        ])

    def test_finite_unlimited(self):
        _check_permutations(self, [
            Case(
                Finite(3, 7), unlimited,
                union=PosNeg(unlimited, empty),
                intersection=PosNeg(Finite(3, 7), unlimited),
            ),
        ])

    def test_finite_finite(self):
        _check_permutations(self, [
            Case(
                Finite(2, 3), Finite(5, 9),
                union=PosNeg(Finite(2, 9), unlimited),
                intersection=PosNeg(empty, unlimited),
            ),
            Case(
                Finite(2, 4), Finite(5, 9),
                union=PosNeg(Finite(2, 9), unlimited),
                intersection=PosNeg(empty, unlimited),
            ),
            Case(
                Finite(2, 5), Finite(5, 9),
                union=PosNeg(Finite(2, 9), unlimited),
                intersection=PosNeg(point(5), unlimited),
            ),
            Case(
                Finite(2, 6), Finite(5, 9),
                union=PosNeg(Finite(2, 9), unlimited),
                intersection=PosNeg(Finite(5, 6), unlimited),
            ),
            Case(
                Finite(2, 7), Finite(5, 9),
                union=PosNeg(Finite(2, 9), unlimited),
                intersection=PosNeg(Finite(5, 7), unlimited),
            ),
            Case(
                Finite(2, 8), Finite(5, 9),
                union=PosNeg(Finite(2, 9), unlimited),
                intersection=PosNeg(Finite(5, 8), unlimited),
            ),
            Case(
                Finite(2, 9), Finite(5, 9),
                union=PosNeg(Finite(2, 9), unlimited),
                intersection=PosNeg(Finite(5, 9), unlimited),
            ),
            Case(
                Finite(2, 10), Finite(5, 9),
                union=PosNeg(Finite(2, 10), unlimited),
                intersection=PosNeg(Finite(5, 9), unlimited),
            ),
            Case(
                Finite(2, 11), Finite(5, 9),
                union=PosNeg(Finite(2, 11), unlimited),
                intersection=PosNeg(Finite(5, 9), unlimited),
            ),
            # same lower
            Case(
                Finite(5, 6), Finite(5, 9),
                union=PosNeg(Finite(5, 9), unlimited),
                intersection=PosNeg(Finite(5, 6), unlimited),
            ),
            Case(
                Finite(5, 7), Finite(5, 9),
                union=PosNeg(Finite(5, 9), unlimited),
                intersection=PosNeg(Finite(5, 7), unlimited),
            ),
            Case(
                Finite(5, 8), Finite(5, 9),
                union=PosNeg(Finite(5, 9), unlimited),
                intersection=PosNeg(Finite(5, 8), unlimited),
            ),
            Case(
                Finite(5, 9), Finite(5, 9),
                union=PosNeg(Finite(5, 9), unlimited),
                intersection=PosNeg(Finite(5, 9), unlimited),
            ),
            Case(
                Finite(5, 10), Finite(5, 9),
                union=PosNeg(Finite(5, 10), unlimited),
                intersection=PosNeg(Finite(5, 9), unlimited),
            ),
            Case(
                Finite(5, 11), Finite(5, 9),
                union=PosNeg(Finite(5, 11), unlimited),
                intersection=PosNeg(Finite(5, 9), unlimited),
            ),
            # lower inside the other
            Case(
                Finite(7, 8), Finite(5, 9),
                union=PosNeg(Finite(5, 9), unlimited),
                intersection=PosNeg(Finite(7, 8), unlimited),
            ),
            Case(
                Finite(7, 9), Finite(5, 9),
                union=PosNeg(Finite(5, 9), unlimited),
                intersection=PosNeg(Finite(7, 9), unlimited),
            ),
            Case(
                Finite(7, 10), Finite(5, 9),
                union=PosNeg(Finite(5, 10), unlimited),
                intersection=PosNeg(Finite(7, 9), unlimited),
            ),
            Case(
                Finite(7, 11), Finite(5, 9),
                union=PosNeg(Finite(5, 11), unlimited),
                intersection=PosNeg(Finite(7, 9), unlimited),
            ),
            # same upper,lower
            Case(
                Finite(9, 10), Finite(5, 9),
                union=PosNeg(Finite(5, 10), unlimited),
                intersection=PosNeg(point(9), unlimited),
            ),
            Case(
                Finite(9, 11), Finite(5, 9),
                union=PosNeg(Finite(5, 11), unlimited),
                intersection=PosNeg(point(9), unlimited),
            ),
        ])


def _check_permutations(put: unittest.TestCase, cases: Sequence[Case]):
    for case in cases:
        for args in [(case.a, case.b), (case.b, case.a)]:
            with put.subTest(lhs=str(args[0]), rhs=str(args[1]), combinator='union'):
                union = sut.union(args[0], args[1])
                equals_interval(case.union.pos).apply_with_message(put, union,
                                                                   'union')
                equals_interval(case.union.neg).apply_with_message(put, union.inversion,
                                                                   'inversion of union')
                equals_interval(case.union.pos).apply_with_message(put, union.inversion.inversion,
                                                                   'double inversion of union')

            with put.subTest(lhs=str(args[0]), rhs=str(args[1]), combinator='intersection'):
                intersection = sut.intersection(args[0], args[1])
                equals_interval(case.intersection.pos).apply_with_message(put, intersection,
                                                                          'intersection')
                equals_interval(case.intersection.neg).apply_with_message(put, intersection.inversion,
                                                                          'inversion of intersection')
                equals_interval(case.intersection.pos).apply_with_message(put, intersection.inversion.inversion,
                                                                          'double inversion of intersection')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
