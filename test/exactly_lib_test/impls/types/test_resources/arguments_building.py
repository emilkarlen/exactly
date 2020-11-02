from typing import Sequence

from exactly_lib.definitions import logic
from exactly_lib.util.cli_syntax.elements.argument import OptionName
from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.symbol.test_resources import arguments_building as sym_ab
from exactly_lib_test.test_resources import argument_renderer as arg_r
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer, QuotedStringArgument, \
    BinaryOperator, PrefixOperator
from exactly_lib_test.test_resources.strings import WithToString


def empty() -> ArgumentElementsRenderer:
    return arg_r.EmptyArgument()


def singleton(value: WithToString) -> ArgumentElementsRenderer:
    return arg_r.Singleton(value)


def sequence(arguments: Sequence[WithToString],
             separator: WithToString = None) -> ArgumentElementsRenderer:
    if separator is not None:
        return arg_r.SequenceOfElementsSeparatedByElement(separator, arguments)
    else:
        return arg_r.SequenceOfElements(arguments)


def sequence__r(arguments: Sequence[ArgumentElementsRenderer]) -> ArgumentElementsRenderer:
    return arg_r.SequenceOfArguments(arguments)


def within_paren(expression: ArgumentElementsRenderer) -> ArgumentElementsRenderer:
    return arg_r.SequenceOfArguments([
        arg_r.Singleton('('),
        expression,
        arg_r.Singleton(')'),
    ])


def quoted_string(string_value: str,
                  quote_type: QuoteType = QuoteType.HARD) -> QuotedStringArgument:
    return QuotedStringArgument(string_value, quote_type)


def option(option_name: OptionName,
           argument: WithToString = None) -> ArgumentElementsRenderer:
    return (
        arg_r.OptionArgument(option_name)
        if argument is None
        else
        arg_r.OptionWithArgument(option_name, argument)
    )


def prefix_operator(operator: str, operand: ArgumentElementsRenderer) -> PrefixOperator:
    return PrefixOperator(operator, operand)


def negation(operand: ArgumentElementsRenderer) -> PrefixOperator:
    return PrefixOperator(logic.NOT_OPERATOR_NAME, operand)


def binary_operator(operator: str, operands: Sequence[ArgumentElementsRenderer]) -> BinaryOperator:
    return BinaryOperator(operator, operands)


def conjunction(operands: Sequence[ArgumentElementsRenderer]) -> BinaryOperator:
    if len(operands) < 2:
        raise ValueError('conjunction: expects at least 2 operands')
    return BinaryOperator(logic.AND_OPERATOR_NAME, operands)


def disjunction(operands: Sequence[ArgumentElementsRenderer]) -> BinaryOperator:
    if len(operands) < 2:
        raise ValueError('disjunction: expects at least 2 operands')
    return BinaryOperator(logic.OR_OPERATOR_NAME, operands)


def constant(value: bool) -> ArgumentElementsRenderer:
    return arg_r.SequenceOfElements([logic.CONSTANT_MATCHER,
                                     logic.BOOLEANS[value]])


def symbol_reference(symbol_name: str) -> ArgumentElementsRenderer:
    return sym_ab.SymbolReferenceArgument(symbol_name)
