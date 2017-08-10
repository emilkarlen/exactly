from enum import Enum


class ExpectationType(Enum):
    """
    Tells if an boolean expression is expected to be
    True (POSITIVE) or False (NEGATIVE)
    """
    POSITIVE = 0
    NEGATIVE = 1
