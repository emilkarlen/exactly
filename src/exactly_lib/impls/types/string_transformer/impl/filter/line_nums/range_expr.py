from typing import TypeVar, Generic, Tuple

from .... import names

FromTo = Tuple[int, int]

RET = TypeVar('RET')


class RangeVisitor(Generic[RET]):
    def visit_single_line(self, x: 'SingleLineRange') -> RET:
        raise NotImplementedError('abstract method')

    def visit_lower_limit(self, x: 'LowerLimitRange') -> RET:
        raise NotImplementedError('abstract method')

    def visit_upper_limit(self, x: 'UpperLimitRange') -> RET:
        raise NotImplementedError('abstract method')

    def visit_lower_and_upper_limit(self, x: 'LowerAndUpperLimitRange') -> RET:
        raise NotImplementedError('abstract method')


class Range:
    def accept(self, visitor: RangeVisitor[RET]) -> RET:
        raise NotImplementedError('abstract method')


class SingleLineRange(Range):
    def __init__(self, line_number: int):
        self.line_number = line_number

    def accept(self, visitor: RangeVisitor[RET]) -> RET:
        return visitor.visit_single_line(self)

    def __str__(self) -> str:
        return str(self.line_number)


class LowerLimitRange(Range):
    def __init__(self, lower_limit: int):
        self.lower_limit = lower_limit

    def accept(self, visitor: RangeVisitor[RET]) -> RET:
        return visitor.visit_lower_limit(self)

    def __str__(self) -> str:
        return str(self.lower_limit) + names.LINE_NUMBERS_FILTER__LIMIT_SEPARATOR


class UpperLimitRange(Range):
    def __init__(self, upper_limit: int):
        self.upper_limit = upper_limit

    def accept(self, visitor: RangeVisitor[RET]) -> RET:
        return visitor.visit_upper_limit(self)

    def __str__(self) -> str:
        return names.LINE_NUMBERS_FILTER__LIMIT_SEPARATOR + str(self.upper_limit)


class LowerAndUpperLimitRange(Range):
    def __init__(self,
                 lower_limit: int,
                 upper_limit: int,
                 ):
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

    def accept(self, visitor: RangeVisitor[RET]) -> RET:
        return visitor.visit_lower_and_upper_limit(self)

    def __str__(self) -> str:
        return names.LINE_NUMBERS_FILTER__LIMIT_SEPARATOR.join((str(self.lower_limit),
                                                                str(self.upper_limit)))
