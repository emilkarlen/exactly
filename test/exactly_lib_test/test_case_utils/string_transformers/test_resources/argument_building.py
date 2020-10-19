from abc import ABC, abstractmethod
from typing import List, Sequence

from exactly_lib.test_case_utils.string_transformer import names
from exactly_lib_test.test_resources import argument_renderer as arg_rend
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer
from exactly_lib_test.test_resources.strings import WithToString


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


def single(n: int) -> Range:
    return SingleLineRange(str(n))


def from_(n: int) -> Range:
    return LowerLimitRange(str(n))


def to_(n: int) -> Range:
    return UpperLimitRange(str(n))


def from_to(m: int, n: int) -> Range:
    return LowerAndUpperLimitRange(str(m), str(n))


class FilterVariant(ArgumentElementsRenderer, ABC):
    pass


class FilterLineMatcherVariant(FilterVariant):
    def __init__(self, line_matcher: ArgumentElementsRenderer):
        self.line_matcher = line_matcher

    @property
    def elements(self) -> List[WithToString]:
        return self.line_matcher.elements


class FilterLineNumbersVariant(FilterVariant):
    def __init__(self, range_expr: Sequence[Range]):
        self.range_expr = range_expr

    @property
    def elements(self) -> List[WithToString]:
        return (
                arg_rend.OptionArgument(names.LINE_NUMBERS_FILTER_OPTION.name).elements +
                [str(r) for r in self.range_expr]
        )


class Filter(ArgumentElementsRenderer):
    def __init__(self, variant: FilterVariant):
        self.variant = variant

    @property
    def elements(self) -> List[WithToString]:
        return [names.FILTER_TRANSFORMER_NAME] + self.variant.elements


def filter_line_nums(range_expr: Range) -> ArgumentElementsRenderer:
    return Filter(FilterLineNumbersVariant([range_expr]))


def filter_line_nums__multi(range_expr: Sequence[Range]) -> ArgumentElementsRenderer:
    return Filter(FilterLineNumbersVariant(range_expr))
