import copy
from typing import Optional, Iterable, Set, Dict


class SymbolTableValue:
    """A value in a symbol table, that is assigned to a name."""
    pass


class Entry(tuple):
    """ A value together with the name that is assigned to it. """

    def __new__(cls,
                name: str,
                value: SymbolTableValue):
        return tuple.__new__(cls, (name,
                                   value))

    @property
    def key(self) -> str:
        return self[0]

    @property
    def value(self) -> SymbolTableValue:
        return self[1]


class SymbolTable:
    """
    A generic mutable symbol table.
    
    Generic in the sense that the values stored are of an abstract class.
    Users of the symbol table should sub class this class for concrete values.
    """

    def __init__(self, initial_values: Dict[str, SymbolTableValue] = None):
        self._key_2_value = {} if initial_values is None else initial_values

    @staticmethod
    def empty() -> 'SymbolTable':
        return SymbolTable()

    def add(self, entry: Entry):
        self._key_2_value[entry.key] = entry.value

    def add_all(self, entries: Iterable[Entry]):
        for entry in entries:
            self.add(entry)

    def add_table(self, symbol_table: 'SymbolTable'):
        self._key_2_value.update(symbol_table._key_2_value)

    def put(self, key: str, x: SymbolTableValue):
        self._key_2_value[key] = x

    def contains(self, key: str) -> bool:
        return key in self._key_2_value

    @property
    def names_set(self) -> Set[str]:
        return set(self._key_2_value.keys())

    def lookup(self, name: str) -> SymbolTableValue:
        """
        :raises KeyError: The symbol table does not contain name.
        """
        try:
            return self._key_2_value[name]
        except KeyError:
            raise KeyError('Name not in symbol table: "{}"'.format(name))

    def copy(self):
        return SymbolTable(copy.copy(self._key_2_value))


def empty_symbol_table() -> SymbolTable:
    return SymbolTable()


def symbol_table_with_entries(entries: Iterable[Entry]) -> SymbolTable:
    ret_val = SymbolTable()
    ret_val.add_all(entries)
    return ret_val


def symbol_table_from_none_or_value(symbol_table_or_none: Optional[SymbolTable]) -> SymbolTable:
    return SymbolTable() if symbol_table_or_none is None else symbol_table_or_none
