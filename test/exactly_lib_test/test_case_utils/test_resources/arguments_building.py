from typing import Sequence

from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.util.cli_syntax.elements.argument import OptionName
from exactly_lib_test.symbol.test_resources import arguments_building as sym_ab
from exactly_lib_test.test_case_file_structure.test_resources import arguments_building as fr_ab
from exactly_lib_test.test_case_file_structure.test_resources.arguments_building import RelOptFileRefArgument, \
    FileRefArgument
from exactly_lib_test.test_resources import arguments_building as ab
from exactly_lib_test.test_resources.arguments_building import ArgumentElementRenderer
from exactly_lib_test.test_resources.arguments_building import Stringable


def empty() -> ArgumentElementRenderer:
    return ab.EmptyArgument()


def sequence(arguments: Sequence[Stringable],
             separator: Stringable = None) -> ArgumentElementRenderer:
    if separator is not None:
        return ab.SequenceOfArgumentsSeparatedByArgument(separator, arguments)
    else:
        return ab.SequenceOfArguments(arguments)


def option(option_name: OptionName,
           argument: Stringable = None) -> ArgumentElementRenderer:
    if argument is None:
        return ab.OptionArgument(option_name)
    else:
        return ab.OptionWithArgument(option_name, argument)


def symbol_reference(symbol_name: str) -> ArgumentElementRenderer:
    return sym_ab.SymbolReferenceArgument(symbol_name)


def rel_option_type(relativity: RelOptionType) -> ArgumentElementRenderer:
    return fr_ab.rel_option_type_arg(relativity)


def rel_symbol_option(symbol_name: str) -> ArgumentElementRenderer:
    return fr_ab.rel_symbol_arg(symbol_name)


def file_ref(file_name: Stringable,
             relativity: ArgumentElementRenderer = None) -> FileRefArgument:
    return FileRefArgument(file_name, relativity)


def file_ref_rel_opt(file_name: str,
                     relativity: RelOptionType) -> RelOptFileRefArgument:
    return RelOptFileRefArgument(file_name, relativity)
