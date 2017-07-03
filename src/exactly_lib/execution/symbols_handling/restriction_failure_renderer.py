from exactly_lib.symbol.concrete_restrictions import FailureOfDirectReference, FailureOfIndirectReference
from exactly_lib.symbol.value_restriction import FailureInfo
from exactly_lib.util import error_message_format
from exactly_lib.util.symbol_table import SymbolTable


def error_message(failing_symbol: str, symbols: SymbolTable, failure: FailureInfo) -> str:
    """
    Renders an error for presentation to the user
    """
    if isinstance(failure, FailureOfDirectReference):
        return failure.error_message
    elif isinstance(failure, FailureOfIndirectReference):
        blank_line_separated_parts = []
        if failure.meaning_of_failure:
            blank_line_separated_parts.append(failure.meaning_of_failure)
        blank_line_separated_parts.append(failure.error_message)
        blank_line_separated_parts.extend(_path_to_failing_symbol(failing_symbol,
                                                                  failure.path_to_failing_symbol,
                                                                  symbols))
        return _concat_parts(blank_line_separated_parts)


def _concat_parts(blank_line_separated_parts: list) -> str:
    parts = [part + '\n' for part in blank_line_separated_parts[:-1]]
    parts.append(blank_line_separated_parts[-1])
    return '\n'.join(parts)


def _path_to_failing_symbol(failing_symbol: str, path_to_failing_symbol: list, symbols: SymbolTable) -> list:
    def line_ref_of_symbol(symbol_name: str) -> str:
        value_container = symbols.lookup(symbol_name)
        return error_message_format.source_line(value_container.definition_source)

    ret_val = []
    path_to_failing_symbol = [failing_symbol] + path_to_failing_symbol
    ret_val.append('Referenced via')
    ret_val.append('\n'.join(map(line_ref_of_symbol, path_to_failing_symbol)))
    return ret_val
