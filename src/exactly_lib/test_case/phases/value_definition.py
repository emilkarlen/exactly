class ValueUsage(object):
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name


class ValueReference(ValueUsage):
    pass


class ValueDefinition(ValueUsage):
    def __init__(self, name: str):
        super().__init__(name)


class SymbolTable:
    """
    Dictionary of value definitions defined by instructions.

    Mutable.
    """

    def __init__(self, initial_values: dict = {}):
        """
        :param initial_values: dictionary str -> ValueDefinition
        """
        self._name_2_value = dict(initial_values)

    def add(self, x: ValueDefinition):
        self._name_2_value[x.name] = x

    def contains(self, name: str) -> bool:
        return name in self._name_2_value

    @property
    def names_set(self) -> set:
        return set(self._name_2_value.keys())


def empty_symbol_table() -> SymbolTable:
    return SymbolTable()


def singleton_symbol_table(element: ValueDefinition) -> SymbolTable:
    return SymbolTable({element.name: element})
