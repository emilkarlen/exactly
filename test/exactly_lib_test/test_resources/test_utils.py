from typing import TypeVar, Generic

EXPECTED = TypeVar('EXPECTED')
ACTUAL = TypeVar('ACTUAL')


class EA:
    """One expected value and one actual value."""

    def __init__(self,
                 expected,
                 actual):
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


class NIE:
    """A name, one expected value and one input value."""

    def __init__(self,
                 name: str,
                 expected_value,
                 input_value):
        self.name = name
        self.expected_value = expected_value
        self.input_value = input_value
