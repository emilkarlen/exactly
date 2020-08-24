from abc import ABC, abstractmethod
from typing import List, Sequence

from exactly_lib.definitions import logic
from exactly_lib.symbol import symbol_syntax
from exactly_lib.test_case_utils.regex import parse_regex
from exactly_lib.util import collection
from exactly_lib.util.parse import token
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer, Singleton, \
    BinaryOperator
from exactly_lib_test.test_resources.strings import WithToString

PAREN_R = Singleton(')')

PAREN_L = Singleton('(')


class MatcherArgument(ArgumentElementsRenderer, ABC):
    """Generate source using __str__"""
    pass


class OfArgumentList(ArgumentElementsRenderer):
    def __init__(self, argument_list: MatcherArgument):
        self.argument_list = argument_list

    def __str__(self) -> str:
        return str(self.argument_list)

    @property
    def elements(self) -> List[WithToString]:
        return self.argument_list.elements


class Constant(MatcherArgument):
    def __init__(self, value: bool):
        self.value = value

    @property
    def elements(self) -> List:
        return [logic.CONSTANT_MATCHER, logic.BOOLEANS[self.value]]


class SymbolReferenceWReferenceSyntax(MatcherArgument):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    def elements(self) -> List:
        return [symbol_syntax.symbol_reference_syntax_for_name(self.symbol_name)]


class BinaryOperatorMatcher(MatcherArgument, BinaryOperator, ABC):
    def __init__(self,
                 operator: str,
                 operands: Sequence[MatcherArgument]):
        super().__init__(operator, operands)
        self._operands = operands

    @property
    def operands(self) -> Sequence[MatcherArgument]:
        return self._operands


def conjunction(operands: Sequence[MatcherArgument]) -> BinaryOperatorMatcher:
    return BinaryOperatorMatcher(logic.AND_OPERATOR_NAME, operands)


def disjunction(operands: Sequence[MatcherArgument]) -> BinaryOperatorMatcher:
    return BinaryOperatorMatcher(logic.OR_OPERATOR_NAME, operands)


class Parenthesis(MatcherArgument):
    def __init__(self, expression: MatcherArgument):
        self.expression = expression

    @property
    def elements(self) -> List[WithToString]:
        return concat_elements([
            PAREN_L,
            self.expression,
            PAREN_R,
        ])


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
            ret_val.insert(0, parse_regex.IGNORE_CASE_OPTION)

        return ret_val


def quote_if_unquoted_with_space(s: str) -> str:
    if ' ' in s and s[0] not in token.QUOTE_CHARS:
        return token.HARD_QUOTE_CHAR + s + token.HARD_QUOTE_CHAR
    else:
        return s


def value_error_if_empty(operator_name: str,
                         matchers: List[MatcherArgument]):
    if len(matchers) == 0:
        raise ValueError(operator_name +
                         ' must have at least one matcher')


def value_error_if_empty__and(matchers: List[MatcherArgument]):
    value_error_if_empty(logic.AND_OPERATOR_NAME,
                         matchers)


def value_error_if_empty__or(matchers: List[MatcherArgument]):
    value_error_if_empty(logic.OR_OPERATOR_NAME,
                         matchers)


def concat_and_intersperse_non_empty_list(operator_name: str,
                                          matchers: List[MatcherArgument]) -> List[WithToString]:
    ret_val = matchers[0].elements
    for matcher in matchers[1:]:
        ret_val.append(operator_name)
        ret_val += matcher.elements
    return ret_val


def concat_elements(matchers: Sequence[MatcherArgument]) -> List[WithToString]:
    return collection.concat_list([
        matcher.elements
        for matcher in matchers
    ])
