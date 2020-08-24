from typing import Sequence

from exactly_lib.definitions import logic
from exactly_lib.util.cli_syntax.elements.argument import OptionName
from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.symbol.test_resources import arguments_building as sym_ab
from exactly_lib_test.test_resources import arguments_building as ab
from exactly_lib_test.test_resources.arguments_building import ArgumentElementsRenderer, QuotedStringArgument, \
    BinaryOperator, PrefixOperator
from exactly_lib_test.test_resources.strings import WithToString


def empty() -> ArgumentElementsRenderer:
    return ab.EmptyArgument()


def singleton(value: WithToString) -> ArgumentElementsRenderer:
    return ab.Singleton(value)


def sequence(arguments: Sequence[WithToString],
             separator: WithToString = None) -> ArgumentElementsRenderer:
    if separator is not None:
        return ab.SequenceOfElementsSeparatedByElement(separator, arguments)
    else:
        return ab.SequenceOfElements(arguments)


def sequence__r(arguments: Sequence[ArgumentElementsRenderer]) -> ArgumentElementsRenderer:
    return ab.SequenceOfArguments(arguments)


def quoted_string(string_value: str,
                  quote_type: QuoteType = QuoteType.HARD) -> QuotedStringArgument:
    return QuotedStringArgument(string_value, quote_type)


def option(option_name: OptionName,
           argument: WithToString = None) -> ArgumentElementsRenderer:
    return (
        ab.OptionArgument(option_name)
        if argument is None
        else
        ab.OptionWithArgument(option_name, argument)
    )


def prefix_operator(operator: str, operand: ArgumentElementsRenderer) -> PrefixOperator:
    return PrefixOperator(operator, operand)


def negation(operand: ArgumentElementsRenderer) -> PrefixOperator:
    return PrefixOperator(logic.NOT_OPERATOR_NAME, operand)


def binary_operator(operator: str, operands: Sequence[ArgumentElementsRenderer]) -> BinaryOperator:
    return BinaryOperator(operator, operands)


def conjunction(operands: Sequence[ArgumentElementsRenderer]) -> BinaryOperator:
    return BinaryOperator(logic.AND_OPERATOR_NAME, operands)


def disjunction(operands: Sequence[ArgumentElementsRenderer]) -> BinaryOperator:
    return BinaryOperator(logic.OR_OPERATOR_NAME, operands)


def symbol_reference(symbol_name: str) -> ArgumentElementsRenderer:
    return sym_ab.SymbolReferenceArgument(symbol_name)
