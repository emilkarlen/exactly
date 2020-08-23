from typing import Sequence

from exactly_lib.definitions import logic
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.util.cli_syntax.elements.argument import OptionName
from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.symbol.test_resources import arguments_building as sym_ab
from exactly_lib_test.test_case_file_structure.test_resources import arguments_building as fr_ab
from exactly_lib_test.test_case_file_structure.test_resources.arguments_building import RelOptPathArgument, \
    PathArgument, path_argument
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
    if argument is None:
        return ab.OptionArgument(option_name)
    else:
        return ab.OptionWithArgument(option_name, argument)


def prefix_operator(operator: str, operand: ArgumentElementsRenderer) -> PrefixOperator:
    return PrefixOperator(operator, operand)


def binary_operator(operator: str, operands: Sequence[ArgumentElementsRenderer]) -> BinaryOperator:
    return BinaryOperator(operator, operands)


def conjunction(operands: Sequence[ArgumentElementsRenderer]) -> BinaryOperator:
    return BinaryOperator(logic.AND_OPERATOR_NAME, operands)


def disjunction(operands: Sequence[ArgumentElementsRenderer]) -> BinaryOperator:
    return BinaryOperator(logic.OR_OPERATOR_NAME, operands)


def symbol_reference(symbol_name: str) -> ArgumentElementsRenderer:
    return sym_ab.SymbolReferenceArgument(symbol_name)


def rel_option_type(relativity: RelOptionType) -> ArgumentElementsRenderer:
    return fr_ab.rel_option_type_arg(relativity)


def rel_symbol_option(symbol_name: str) -> ArgumentElementsRenderer:
    return fr_ab.rel_symbol_arg(symbol_name)


def path(file_name: WithToString,
         relativity: ArgumentElementsRenderer = None) -> PathArgument:
    return path_argument(file_name, relativity)


def path_rel_opt(file_name: str,
                 relativity: RelOptionType) -> RelOptPathArgument:
    return RelOptPathArgument(file_name, relativity)
