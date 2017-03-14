from exactly_lib.util.symbol_table import SymbolTable


def symbol_table_from_none_or_value(symbol_table_or_none: SymbolTable) -> SymbolTable:
    return SymbolTable() if symbol_table_or_none is None else symbol_table_or_none
