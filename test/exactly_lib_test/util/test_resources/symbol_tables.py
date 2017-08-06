from exactly_lib.util.symbol_table import SymbolTable


def symbol_table_from_entries(entries: iter) -> SymbolTable:
    """
    :param entries: [`Entry`]
    """
    elements = [(entry.key, entry.value)
                for entry in entries]
    return SymbolTable(dict(elements))
