import itertools

from typing import List, Sequence

from exactly_lib.common.err_msg import rendering
from exactly_lib.common.err_msg.definitions import Blocks, single_str_block
from exactly_lib.symbol.data.restrictions.reference_restrictions import FailureOfDirectReference, \
    FailureOfIndirectReference
from exactly_lib.symbol.data.value_restriction import ValueRestrictionFailure
from exactly_lib.symbol.err_msg import error_messages
from exactly_lib.symbol.lookups import lookup_container
from exactly_lib.symbol.resolver_structure import SymbolContainer
from exactly_lib.symbol.restriction import FailureInfo, InvalidTypeCategoryFailure, InvalidValueTypeFailure
from exactly_lib.type_system.value_type import TYPE_CATEGORY_2_VALUE_TYPE_SEQUENCE
from exactly_lib.util.symbol_table import SymbolTable


def error_message(failing_symbol: str, symbols: SymbolTable, failure: FailureInfo) -> str:
    """
    Renders an error for presentation to the user
    """
    if isinstance(failure, FailureOfDirectReference):
        return error_message_for_direct_reference(failure.error)
    elif isinstance(failure, FailureOfIndirectReference):
        return _of_indirect(failing_symbol, symbols, failure)
    elif isinstance(failure, InvalidTypeCategoryFailure):
        return _of_invalid_type_category(failing_symbol, symbols, failure)
    elif isinstance(failure, InvalidValueTypeFailure):
        return _of_invalid_value_type(failing_symbol, symbols, failure)
    else:
        raise TypeError('Unknown type of {}: {}'.format(str(FailureInfo),
                                                        str(failure)))


def _of_invalid_type_category(failing_symbol: str,
                              symbols: SymbolTable,
                              failure: InvalidTypeCategoryFailure) -> str:
    value_restriction_failure = error_messages.invalid_type_msg(TYPE_CATEGORY_2_VALUE_TYPE_SEQUENCE[failure.expected],
                                                                failing_symbol,
                                                                lookup_container(symbols, failing_symbol))
    return _concat_parts(_as_lines(value_restriction_failure))


def _as_lines(x: ValueRestrictionFailure) -> List[str]:
    parts = [x.message]
    if x.how_to_fix:
        parts.append(x.how_to_fix)
    return ['\n\n'.join(parts)]


def _of_invalid_value_type(failing_symbol: str,
                           symbols: SymbolTable,
                           failure: InvalidValueTypeFailure) -> str:
    value_restriction_failure = error_messages.invalid_type_msg([failure.expected],
                                                                failing_symbol,
                                                                lookup_container(symbols, failing_symbol))
    return _concat_parts(_as_lines(value_restriction_failure))


def error_message_for_direct_reference(error: ValueRestrictionFailure) -> str:
    blank_line_separated_parts = [error.message]
    blank_line_separated_parts.extend(_final_how_to_fix(error))
    return _concat_parts(blank_line_separated_parts)


def _of_indirect(failing_symbol: str,
                 symbols: SymbolTable,
                 failure: FailureOfIndirectReference) -> str:
    blocks = []
    if failure.meaning_of_failure:
        blocks.append(single_str_block(failure.meaning_of_failure))
    error = failure.error
    blocks.append(single_str_block(error.message))
    blocks += _path_to_failing_symbol(failing_symbol,
                                      failure.path_to_failing_symbol,
                                      symbols)
    blocks += _how_to_fix_blocks(error)
    return rendering.blocks_as_str(blocks)


def _path_to_failing_symbol(failing_symbol: str,
                            path_to_failing_symbol: List[str],
                            symbols: SymbolTable) -> Blocks:
    def line_ref_of_symbol(symbol_name: str) -> Blocks:
        container = symbols.lookup(symbol_name)
        assert isinstance(container, SymbolContainer), 'Only known type of SymbolTableValue'
        return error_messages._builtin_or_user_defined_source_blocks(container.source_location)

    path_to_failing_symbol = [failing_symbol] + path_to_failing_symbol

    ret_val = [
        single_str_block('Referenced via')
    ]

    ret_val += itertools.chain.from_iterable(map(line_ref_of_symbol, path_to_failing_symbol))

    return ret_val


def _final_how_to_fix(error: ValueRestrictionFailure) -> list:
    if error.how_to_fix:
        return ['\n' + error.how_to_fix]
    return []


def _how_to_fix_blocks(error: ValueRestrictionFailure) -> Blocks:
    if error.how_to_fix:
        return [[error.how_to_fix]]
    return []


def _concat_parts(blank_line_separated_parts: Sequence[str]) -> str:
    parts = [part + '\n' for part in blank_line_separated_parts[:-1]]
    parts.append(blank_line_separated_parts[-1])
    return '\n'.join(parts)
