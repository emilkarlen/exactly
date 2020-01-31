from typing import TypeVar, Generic

EXPECTED = TypeVar('EXPECTED')
INPUT = TypeVar('INPUT')
ACTUAL = TypeVar('ACTUAL')
ARRANGEMENT = TypeVar('ARRANGEMENT')


class EA(Generic[EXPECTED, ACTUAL]):
    """One expected value and one actual value."""

    def __init__(self,
                 expected: EXPECTED,
                 actual: ACTUAL):
        self.expected = expected
        self.actual = actual


class NEA(Generic[EXPECTED, ACTUAL]):
    """A name, one expected value and one actual value."""

    def __init__(self,
                 name: str,
                 expected: EXPECTED,
                 actual: ACTUAL):
        self.name = name
        self.expected = expected
        self.actual = actual

    @staticmethod
    def new_identical_expected_and_actual(name: str, expected: EXPECTED) -> 'NEA[EXPECTED, ACTUAL]':
        return NEA(name, expected, expected)


class NExArr(Generic[EXPECTED, ACTUAL]):
    """A name, one expected value and one actual value."""

    def __init__(self,
                 name: str,
                 expected: EXPECTED,
                 arrangement: ARRANGEMENT):
        self.name = name
        self.expected = expected
        self.arrangement = arrangement


class NArrEx(Generic[ACTUAL, EXPECTED]):
    """A name, one expected value and one actual value."""

    def __init__(self,
                 name: str,
                 arrangement: ARRANGEMENT,
                 expectation: EXPECTED,
                 ):
        self.name = name
        self.arrangement = arrangement
        self.expectation = expectation


class NIE(Generic[INPUT, EXPECTED]):
    """A name, one expected value and one input value."""

    def __init__(self,
                 name: str,
                 expected_value: EXPECTED,
                 input_value: INPUT):
        self.name = name
        self.expected_value = expected_value
        self.input_value = input_value
