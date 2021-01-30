from abc import ABC, abstractmethod
from typing import Sequence

from exactly_lib_test.impls.types.string_transformer.filter.line_numbers.test_resources import argument_building as ab
from exactly_lib_test.impls.types.string_transformer.filter.line_numbers.test_resources.argument_building \
    import Range


class ValidRange(ABC):
    @property
    @abstractmethod
    def is_const_empty(self) -> bool:
        pass

    @property
    @abstractmethod
    def as_arg(self) -> Range:
        pass


def range_is_const_empty(lower_limit: int,
                         upper_limit: int) -> bool:
    if upper_limit == 0:
        return True
    elif lower_limit >= 0 and upper_limit > 0:
        return lower_limit > upper_limit
    elif lower_limit < 0 and upper_limit < 0:
        return lower_limit > upper_limit
    else:
        return False


def ranges_is_const_empty(ranges: Sequence[ValidRange]) -> bool:
    return all([range_.is_const_empty for range_ in ranges])


class SingleLineVRange(ValidRange):
    def __init__(self, line_number: int):
        self.line_number = line_number

    @property
    def is_const_empty(self) -> bool:
        return self.line_number == 0

    @property
    def as_arg(self) -> Range:
        return ab.SingleLineRange(str(self.line_number))


class LowerLimitVRange(ValidRange):
    def __init__(self, lower_limit: int):
        self.lower_limit = lower_limit

    @property
    def is_const_empty(self) -> bool:
        return False

    @property
    def as_arg(self) -> Range:
        return ab.LowerLimitRange(str(self.lower_limit))


class UpperLimitVRange(ValidRange):
    def __init__(self, upper_limit: int):
        self.upper_limit = upper_limit

    @property
    def is_const_empty(self) -> bool:
        return self.upper_limit == 0

    @property
    def as_arg(self) -> Range:
        return ab.UpperLimitRange(str(self.upper_limit))


class LowerAndUpperLimitVRange(ValidRange):
    def __init__(self,
                 lower_limit: int,
                 upper_limit: int,
                 ):
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

    @property
    def is_const_empty(self) -> bool:
        return range_is_const_empty(self.lower_limit, self.upper_limit)

    @property
    def as_arg(self) -> Range:
        return ab.LowerAndUpperLimitRange(str(self.lower_limit),
                                          str(self.upper_limit))


def single(n: int) -> ValidRange:
    return SingleLineVRange(n)


def from_(n: int) -> ValidRange:
    return LowerLimitVRange(n)


def to_(n: int) -> ValidRange:
    return UpperLimitVRange(n)


def from_to(lower: int, upper: int) -> ValidRange:
    return LowerAndUpperLimitVRange(lower, upper)
