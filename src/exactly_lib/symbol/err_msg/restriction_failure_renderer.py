from exactly_lib.help_texts import type_system
from exactly_lib.symbol.data.restrictions.reference_restrictions import FailureOfDirectReference, \
    FailureOfIndirectReference
from exactly_lib.symbol.data.value_restriction import ValueRestrictionFailure
from exactly_lib.symbol.resolver_structure import SymbolContainer
from exactly_lib.symbol.restriction import FailureInfo, InvalidTypeCategoryFailure, InvalidValueTypeFailure
from exactly_lib.util import error_message_format
from exactly_lib.util.symbol_table import SymbolTable


def error_message(failing_symbol: str, symbols: SymbolTable, failure: FailureInfo) -> str:
    """
    Renders an error for presentation to the user
    """
    if isinstance(failure, FailureOfDirectReference):
        blank_line_separated_parts = error_message_for_direct_reference(failure.error)
    elif isinstance(failure, FailureOfIndirectReference):
        blank_line_separated_parts = _of_indirect(failing_symbol, symbols, failure)
    elif isinstance(failure, InvalidTypeCategoryFailure):
        blank_line_separated_parts = _of_invalid_type_category(failing_symbol, symbols, failure)
    elif isinstance(failure, InvalidValueTypeFailure):
        blank_line_separated_parts = _of_invalid_value_type(failing_symbol, symbols, failure)
    else:
        raise TypeError('Unknown type of {}: {}'.format(str(FailureInfo),
                                                        str(failure)))
    return _concat_parts(blank_line_separated_parts)


def _of_invalid_type_category(failing_symbol: str, symbols: SymbolTable, failure: InvalidTypeCategoryFailure) -> list:
    msg = _expected_actual(failing_symbol,
                           type_system.TYPE_CATEGORY_NAME[failure.expected],
                           type_system.TYPE_CATEGORY_NAME[failure.actual],
                           )
    blank_line_separated_parts = [msg]
    return blank_line_separated_parts


def _of_invalid_value_type(failing_symbol: str, symbols: SymbolTable, failure: InvalidValueTypeFailure) -> list:
    msg = _expected_actual(failing_symbol,
                           type_system.TYPE_INFO_DICT[failure.expected].identifier,
                           type_system.TYPE_INFO_DICT[failure.actual].identifier,
                           )
    blank_line_separated_parts = [msg]
    return blank_line_separated_parts


def error_message_for_direct_reference(error: ValueRestrictionFailure) -> list:
    blank_line_separated_parts = [error.message]
    blank_line_separated_parts.extend(_final_how_to_fix(error))
    return blank_line_separated_parts


def _of_indirect(failing_symbol: str, symbols: SymbolTable, failure: FailureOfIndirectReference) -> list:
    blank_line_separated_parts = []
    if failure.meaning_of_failure:
        blank_line_separated_parts.append(failure.meaning_of_failure)
    error = failure.error
    blank_line_separated_parts.append(error.message)
    blank_line_separated_parts.extend(_path_to_failing_symbol(failing_symbol,
                                                              failure.path_to_failing_symbol,
                                                              symbols))
    blank_line_separated_parts.extend(_final_how_to_fix(error))
    return blank_line_separated_parts


def _path_to_failing_symbol(failing_symbol: str, path_to_failing_symbol: list, symbols: SymbolTable) -> list:
    def line_ref_of_symbol(symbol_name: str) -> str:
        container = symbols.lookup(symbol_name)
        assert isinstance(container, SymbolContainer), 'Only known type of SymbolTableValue'
        return error_message_format.source_line_of_symbol(container.definition_source)

    ret_val = []
    path_to_failing_symbol = [failing_symbol] + path_to_failing_symbol
    ret_val.append('\n' + 'Referenced via')
    ret_val.append('\n'.join(map(line_ref_of_symbol, path_to_failing_symbol)))
    return ret_val


def _final_how_to_fix(error: ValueRestrictionFailure) -> list:
    if error.how_to_fix:
        return ['\n' + error.how_to_fix]
    return []


def _concat_parts(blank_line_separated_parts: list) -> str:
    parts = [part + '\n' for part in blank_line_separated_parts[:-1]]
    parts.append(blank_line_separated_parts[-1])
    return '\n'.join(parts)


def _expected_actual(failing_symbol: str, expected: str, actual: str) -> str:
    # TODO: replace with other utilities for expected/actual
    return '\n'.join([
        'Invalid type of symbol {}'.format(failing_symbol),
        '',
        'Expected : ' + expected,
        'Found    : ' + actual,
    ])
