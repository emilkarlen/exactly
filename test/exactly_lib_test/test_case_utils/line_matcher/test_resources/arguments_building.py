from abc import ABC, abstractmethod
from typing import List

from exactly_lib.definitions import expression
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib.util.logic_types import ExpectationType


class LineMatcherArg(ABC):
    """Generate source using __str__"""
    pass

    def __str__(self):
        return ' '.join([str(element) for element in self.elements])

    @property
    @abstractmethod
    def elements(self) -> List:
        pass


class Custom(LineMatcherArg):
    def __init__(self, matcher: str):
        self.matcher = matcher

    @property
    def elements(self) -> List:
        return [self.matcher]


class LineNum(LineMatcherArg):
    def __init__(self, int_condition: str):
        self._int_condition = int_condition

    @property
    def elements(self) -> List:
        return [parse_line_matcher.LINE_NUMBER_MATCHER_NAME,
                self._int_condition,
                ]


class Matches(LineMatcherArg):
    def __init__(self, regex: str):
        self.regex = regex

    @property
    def elements(self) -> List:
        return [parse_line_matcher.REGEX_MATCHER_NAME,
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


class And(LineMatcherArg):
    def __init__(self, matchers: List[LineMatcherArg]):
        self.matchers = matchers
        if len(matchers) == 0:
            raise ValueError(expression.AND_OPERATOR_NAME +
                             ' must have at least one matcher')

    @property
    def elements(self) -> List:
        ret_val = self.matchers[0].elements
        for matcher in self.matchers[1:]:
            ret_val.append(expression.AND_OPERATOR_NAME)
            ret_val += matcher.elements
        return ret_val


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
