class Value:
    pass


class Entry(tuple):
    def __new__(cls,
                name: str,
                value: Value):
        return tuple.__new__(cls, (name,
                                   value))

    @property
    def name(self) -> str:
        return self[0]

    @property
    def value(self) -> Value:
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
        self._name_2_value = {} if initial_values is None else initial_values

    def add(self, entry: Entry):
        self._name_2_value[entry.name] = entry.value

    def put(self, name: str, x: Value):
        self._name_2_value[name] = x

    def contains(self, name: str) -> bool:
        return name in self._name_2_value

    @property
    def names_set(self) -> set:
        return set(self._name_2_value.keys())

    def lookup(self, name: str) -> Value:
        """
        :raises KeyError: The symbol table does not contain name.
        """
        return self._name_2_value[name]


def empty_symbol_table() -> SymbolTable:
    return SymbolTable()


def singleton_symbol_table(entry: Entry) -> SymbolTable:
    return SymbolTable({entry.name: entry.value})
