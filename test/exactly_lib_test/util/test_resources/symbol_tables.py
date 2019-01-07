from typing import Iterable

from exactly_lib.util.symbol_table import SymbolTable, Entry


def symbol_table_from_entries(entries: Iterable[Entry]) -> SymbolTable:
    elements = [(entry.key, entry.value)
                for entry in entries]
    return SymbolTable(dict(elements))
