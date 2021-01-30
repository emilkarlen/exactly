from abc import ABC, abstractmethod

from exactly_lib.impls.types.string_transformer import names


class Range(ABC):
    LIMIT_TOKEN = names.LINE_NUMBERS_FILTER__LIMIT_SEPARATOR

    @abstractmethod
    def __str__(self) -> str:
        pass


class CustomRange(Range):
    def __init__(self, range_expr: str):
        self.range_expr = range_expr

    def __str__(self) -> str:
        return self.range_expr


class SingleLineRange(Range):
    def __init__(self, line_number: str):
        self.line_number = line_number

    def __str__(self) -> str:
        return self.line_number


class LowerLimitRange(Range):
    def __init__(self, lower_limit: str):
        self.lower_limit = lower_limit

    def __str__(self) -> str:
        return self.lower_limit + self.LIMIT_TOKEN


class UpperLimitRange(Range):
    def __init__(self, upper_limit: str):
        self.upper_limit = upper_limit

    def __str__(self) -> str:
        return self.LIMIT_TOKEN + self.upper_limit


class LowerAndUpperLimitRange(Range):
    def __init__(self,
                 lower_limit: str,
                 upper_limit: str,
                 ):
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

    def __str__(self) -> str:
        return self.lower_limit + self.LIMIT_TOKEN + self.upper_limit
