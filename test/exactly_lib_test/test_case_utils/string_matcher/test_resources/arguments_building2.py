from typing import Sequence

from exactly_lib.definitions import logic
from exactly_lib.definitions.instruction_arguments import WITH_TRANSFORMED_CONTENTS_OPTION_NAME
from exactly_lib.test_case_utils.string_matcher import matcher_options
from exactly_lib.util.cli_syntax.option_syntax import option_syntax
from exactly_lib.util.logic_types import Quantifier
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments


class StringMatcherArg:
    """Generate source using __str__"""
    pass

    @property
    def as_arguments(self) -> Arguments:
        return Arguments(str(self))


class Empty(StringMatcherArg):
    def __str__(self):
        return matcher_options.EMPTY_ARGUMENT


class SymbolReference(StringMatcherArg):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    def __str__(self):
        return self.symbol_name


class Transformed(StringMatcherArg):
    def __init__(self,
                 transformer: str,
                 on_transformed: StringMatcherArg):
        self.transformer = transformer
        self.on_transformed = on_transformed

    def __str__(self):
        return ' '.join([
            option_syntax(WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
            self.transformer,
            str(self.on_transformed),
        ])


class NumLines(StringMatcherArg):
    def __init__(self, condition: str):
        self._condition = condition

    def __str__(self):
        return matcher_options.NUM_LINES_ARGUMENT + ' ' + self._condition


class Equals(StringMatcherArg):
    def __init__(self, string_argument: str):
        """
        :param string_argument: Must be a single token.
        """
        self._string_argument = string_argument

    def __str__(self):
        return matcher_options.EQUALS_ARGUMENT + ' ' + self._string_argument


class LineMatches(StringMatcherArg):
    def __init__(self,
                 quantifier: Quantifier,
                 line_matcher: str):
        self.quantifier = quantifier
        self._condition = line_matcher

    def __str__(self):
        return '{any_or_every} {line} {quantifier_separator} {condition}'.format(
            any_or_every=logic.QUANTIFIER_ARGUMENTS[self.quantifier],
            line=matcher_options.LINE_ARGUMENT,
            quantifier_separator=logic.QUANTIFICATION_SEPARATOR_ARGUMENT,
            condition=self._condition,
        )


class Not(StringMatcherArg):
    def __init__(self, matcher: StringMatcherArg):
        self.matcher = matcher

    def __str__(self):
        return logic.NOT_OPERATOR_NAME + ' ' + str(self.matcher)


class Parenthesis(StringMatcherArg):
    def __init__(self, string_matcher: StringMatcherArg):
        self.string_matcher = string_matcher

    def __str__(self):
        return '( {} )'.format(self.string_matcher)


class BinaryOperator(StringMatcherArg):
    def __init__(self,
                 operator: str,
                 operands: Sequence[StringMatcherArg]):
        self.operator = operator
        self.operands = operands

    def __str__(self):
        return (' ' + self.operator + ' ').join([str(op) for op in self.operands])


def conjunction(operands: Sequence[StringMatcherArg]) -> BinaryOperator:
    return BinaryOperator(logic.AND_OPERATOR_NAME, operands)


def disjunction(operands: Sequence[StringMatcherArg]) -> BinaryOperator:
    return BinaryOperator(logic.AND_OPERATOR_NAME, operands)
