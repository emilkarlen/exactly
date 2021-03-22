import unittest
from typing import Callable, Union

from exactly_lib.util.either import Either


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestLeft),
        unittest.makeSuite(TestRight),
    ])


AnyValue = Union[int, str]


class Checker:
    def __init__(self,
                 sut: Either[int, str],
                 check_form__true: Callable[[Either], bool],
                 check_form__false: Callable[[Either], bool],
                 getter__valid: Callable[[Either[int, str]], AnyValue],
                 getter__invalid: Callable[[Either[int, str]], AnyValue],
                 expected_from_getter: AnyValue,
                 ):
        self.sut = sut
        self.check_form__true = check_form__true
        self.check_form__false = check_form__false
        self.getter__valid = getter__valid
        self.getter__invalid = getter__invalid
        self.expected_from_getter = expected_from_getter

    def test_valid_access(self, put: unittest.TestCase):
        put.assertTrue(self.check_form__true(self.sut), 'check form / true')
        put.assertFalse(self.check_form__false(self.sut), 'check form / true')
        value_from_getter = self.getter__valid(self.sut)
        put.assertEqual(self.expected_from_getter, value_from_getter, 'value from valid getter')

    def test_invalid_access(self, put: unittest.TestCase):
        with put.assertRaises(ValueError):
            self.getter__invalid(self.sut)


def _is_left(e: Either) -> bool:
    return e.is_left()


def _is_right(e: Either) -> bool:
    return e.is_right()


def _get_left(e: Either[int, str]) -> int:
    return e.left()


def _get_right(e: Either[int, str]) -> str:
    return e.right()


class TestLeft(unittest.TestCase):
    SUT = Either.of_left(72)
    CHECKER = Checker(
        SUT,
        check_form__true=_is_left,
        check_form__false=_is_right,
        getter__valid=_get_left,
        getter__invalid=_get_right,
        expected_from_getter=72,
    )

    def test_valid_access(self):
        self.CHECKER.test_valid_access(self)

    def test_invalid_access(self):
        self.CHECKER.test_invalid_access(self)


class TestRight(unittest.TestCase):
    SUT = Either.of_right('Snake skin boots')
    CHECKER = Checker(
        SUT,
        check_form__true=_is_right,
        check_form__false=_is_left,
        getter__valid=_get_right,
        getter__invalid=_get_left,
        expected_from_getter='Snake skin boots',
    )

    def test_valid_access(self):
        self.CHECKER.test_valid_access(self)

    def test_invalid_access(self):
        self.CHECKER.test_invalid_access(self)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
