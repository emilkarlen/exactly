from abc import ABC, abstractmethod
from typing import List

from exactly_lib.definitions import expression
from exactly_lib.test_case_utils.parse import parse_reg_ex
from exactly_lib.util.parse import token


class MatcherArg(ABC):
    """Generate source using __str__"""
    pass

    def __str__(self):
        return ' '.join([str(element) for element in self.elements])

    @property
    @abstractmethod
    def elements(self) -> List:
        pass


class MatcherArgComponent(ABC):
    """
    Something that is not a matcher argument on its own - but
    is a part of an argument

    Generate source using __str__
    """

    def __str__(self):
        return ' '.join([str(element) for element in self.elements])

    @property
    @abstractmethod
    def elements(self) -> List:
        pass


class NameRegexComponent(MatcherArgComponent):
    def __init__(self,
                 regex: str,
                 ignore_case: bool = False):
        self.regex = regex
        self.ignore_case = ignore_case

    @property
    def elements(self) -> List:
        ret_val = [quote_if_unquoted_with_space(self.regex)]

        if self.ignore_case:
            ret_val.insert(0, parse_reg_ex.IGNORE_CASE_OPTION)

        return ret_val


def quote_if_unquoted_with_space(s: str) -> str:
    if ' ' in s and s[0] not in token.QUOTE_CHARS:
        return token.HARD_QUOTE_CHAR + s + token.HARD_QUOTE_CHAR
    else:
        return s


def value_error_if_empty(operator_name: str,
                         matchers: List[MatcherArg]):
    if len(matchers) == 0:
        raise ValueError(operator_name +
                         ' must have at least one matcher')


def value_error_if_empty__and(matchers: List[MatcherArg]):
    value_error_if_empty(expression.AND_OPERATOR_NAME,
                         matchers)


def value_error_if_empty__or(matchers: List[MatcherArg]):
    value_error_if_empty(expression.OR_OPERATOR_NAME,
                         matchers)


def concat_and_intersperse_non_empty_list(operator_name: str,
                                          matchers: List[MatcherArg]) -> List:
    ret_val = matchers[0].elements
    for matcher in matchers[1:]:
        ret_val.append(operator_name)
        ret_val += matcher.elements
    return ret_val
