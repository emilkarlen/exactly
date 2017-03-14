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
    Dictionary of value definitions defined by instructions.

    Mutable.
    """

    def __init__(self, initial_values: dict = None):
        """
        :param initial_values: dictionary str -> Value
        """
        self._key_2_value = {} if initial_values is None else initial_values

    def add(self, entry: Entry):
        self._key_2_value[entry.key] = entry.value

    def put(self, key: str, x: SymbolTableValue):
        self._key_2_value[key] = x

    def contains(self, key: str) -> bool:
        return key in self._key_2_value

    @property
    def names_set(self) -> set:
        return set(self._key_2_value.keys())

    def lookup(self, name: str) -> SymbolTableValue:
        """
        :raises KeyError: The symbol table does not contain name.
        """
        try:
            return self._key_2_value[name]
        except KeyError:
            raise KeyError('Name not in symbol table: "{}"'.format(name))


def empty_symbol_table() -> SymbolTable:
    return SymbolTable()


def singleton_symbol_table(entry: Entry) -> SymbolTable:
    return SymbolTable({entry.key: entry.value})
