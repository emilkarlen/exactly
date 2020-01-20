from abc import ABC
from typing import List

from exactly_lib.definitions import expression
from exactly_lib.definitions.primitives import line_matcher
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.test_resources import matcher_argument
from exactly_lib_test.test_resources.matcher_argument import MatcherArgument


class LineMatcherArg(MatcherArgument, ABC):
    pass


class Custom(LineMatcherArg):
    """Argument for building invalid syntax"""

    def __init__(self, matcher: str):
        self.matcher = matcher

    @property
    def elements(self) -> List:
        return [self.matcher]


class SymbolReference(LineMatcherArg):
    def __init__(self, symbol_name: str):
        self._symbol_name = symbol_name

    @property
    def elements(self) -> List:
        return [self._symbol_name]


class LineNum(LineMatcherArg):
    def __init__(self, int_condition: str):
        self._int_condition = int_condition

    @property
    def elements(self) -> List:
        return [line_matcher.LINE_NUMBER_MATCHER_NAME,
                self._int_condition,
                ]


class Matches(LineMatcherArg):
    def __init__(self, regex: str):
        self.regex = regex

    @property
    def elements(self) -> List:
        return [line_matcher.REGEX_MATCHER_NAME,
                self.regex,
                ]


class Not(LineMatcherArg):
    def __init__(self, matcher: LineMatcherArg):
        self.matcher = matcher

    @property
    def elements(self) -> List:
        return [expression.NOT_OPERATOR_NAME,
                str(self.matcher),
                ]


class _BinaryOperatorBase(LineMatcherArg):
    def __init__(self,
                 operator_name: str,
                 matchers: List[LineMatcherArg]):
        self.matchers = matchers
        self.operator_name = operator_name
        matcher_argument.value_error_if_empty(operator_name, matchers)

    @property
    def elements(self) -> List:
        return matcher_argument.concat_and_intersperse_non_empty_list(self.operator_name,
                                                                      self.matchers)


class And(_BinaryOperatorBase):
    def __init__(self, matchers: List[LineMatcherArg]):
        super().__init__(expression.AND_OPERATOR_NAME, matchers)


class Or(_BinaryOperatorBase):
    def __init__(self, matchers: List[LineMatcherArg]):
        super().__init__(expression.OR_OPERATOR_NAME, matchers)


class WithOptionalNegation:
    def __init__(self, matcher: LineMatcherArg):
        self.matcher = matcher

    def get(self, expectation_type: ExpectationType) -> LineMatcherArg:
        if expectation_type is ExpectationType.POSITIVE:
            return self.matcher
        else:
            return Not(self.matcher)

    def get_elements(self, expectation_type: ExpectationType) -> List:
        return self.get(expectation_type).elements


NOT_A_LINE_MATCHER = Custom('%%')
