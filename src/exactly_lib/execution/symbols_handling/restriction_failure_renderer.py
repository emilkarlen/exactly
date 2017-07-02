from exactly_lib.symbol.concrete_restrictions import FailureOfDirectReference, FailureOfIndirectReference
from exactly_lib.symbol.value_restriction import FailureInfo
from exactly_lib.util.symbol_table import SymbolTable


def error_message(failure: FailureInfo, symbols: SymbolTable) -> str:
    """
    Renders an error for presentation to the user
    """
    if isinstance(failure, FailureOfDirectReference):
        return failure.error_message
    elif isinstance(failure, FailureOfIndirectReference):
        line_separated_parts = []
        if failure.meaning_of_failure:
            line_separated_parts.append(failure.meaning_of_failure)
            line_separated_parts.append('')
        line_separated_parts.append(failure.error_message)
        return '\n'.join(line_separated_parts)
