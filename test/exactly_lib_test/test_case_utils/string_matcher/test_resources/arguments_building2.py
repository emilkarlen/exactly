from typing import Sequence, List

from exactly_lib.definitions import logic
from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol import symbol_syntax
from exactly_lib.test_case_utils.string_matcher import matcher_options
from exactly_lib.util.cli_syntax.option_syntax import option_syntax
from exactly_lib.util.logic_types import Quantifier
from exactly_lib_test.section_document.test_resources import parse_source
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments, ArgumentElements
from exactly_lib_test.test_resources.strings import WithToString


class StringMatcherArg:
    """Generate source using __str__"""
    pass

    @property
    def as_arguments(self) -> Arguments:
        return Arguments(str(self))

    @property
    def as_remaining_source(self) -> ParseSource:
        return parse_source.remaining_source(str(self))


class Empty(StringMatcherArg):
    def __str__(self):
        return matcher_options.EMPTY_ARGUMENT


class SymbolReference(StringMatcherArg):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    def __str__(self):
        return self.symbol_name


class SymbolReferenceWithReferenceSyntax(StringMatcherArg):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    def __str__(self):
        return symbol_syntax.symbol_reference_syntax_for_name(self.symbol_name)


class Transformed(StringMatcherArg):
    def __init__(self,
                 transformer: str,
                 on_transformed: StringMatcherArg):
        self.transformer = transformer
        self.on_transformed = on_transformed

    def __str__(self):
        return ' '.join([
            option_syntax(string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
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


class Quantification(StringMatcherArg):
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


class RunProgram(StringMatcherArg):
    def __init__(self, program: ArgumentElements):
        self.program = program

    @property
    def as_argument_elements(self) -> ArgumentElements:
        run_primitive = ArgumentElements([matcher_options.RUN_PROGRAM_ARGUMENT])
        return run_primitive.append_to_first_and_following_lines(self.program)

    def __str__(self):
        return self.as_argument_elements.as_arguments.as_single_string

    @property
    def elements(self) -> List[WithToString]:
        return self.as_argument_elements.as_elements


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
    return BinaryOperator(logic.OR_OPERATOR_NAME, operands)


class Custom(StringMatcherArg):
    def __init__(self, string_matcher: WithToString):
        self.string_matcher = string_matcher

    def __str__(self):
        return str(self.string_matcher)
