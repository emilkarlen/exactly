from abc import ABC
from typing import List, Sequence

from exactly_lib.impls.types.string_transformer import names
from exactly_lib_test.impls.types.string_transformer.filter.line_numbers.test_resources.argument_building import Range
from exactly_lib_test.test_resources import argument_renderer as arg_rend
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer
from exactly_lib_test.test_resources.strings import WithToString


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
