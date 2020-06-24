from enum import Enum


class ExpectationType(Enum):
    """
    Tells if an boolean expression is expected to be
    True (POSITIVE) or False (NEGATIVE)
    """
    POSITIVE = 0
    NEGATIVE = 1


def from_is_negated(is_negated: bool) -> ExpectationType:
    return (
        ExpectationType.NEGATIVE
        if is_negated
        else
        ExpectationType.POSITIVE
    )


class Quantifier(Enum):
    """A logic quantifier"""
    ALL = 1
    EXISTS = 2
