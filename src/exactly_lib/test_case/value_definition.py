from exactly_lib.test_case.file_ref import FileRef
from exactly_lib.util.line_source import Line


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


class ValueInfo(tuple):
    def __new__(cls,
                source: Line,
                file_ref: FileRef):
        return tuple.__new__(cls, (source,
                                   file_ref))


class ValueEntry(tuple):
    def __new__(cls,
                name: str,
                info: ValueInfo):
        return tuple.__new__(cls, (name,
                                   info))

    @property
    def name(self) -> str:
        return self[0]

    @property
    def info(self) -> ValueInfo:
        return self[1]


class SymbolTable:
    """
    Dictionary of value definitions defined by instructions.

    Mutable.
    """

    def __init__(self, initial_values: dict = None):
        """
        :param initial_values: dictionary str -> ValueInfo
        """
        self._name_2_value = {} if initial_values is None else initial_values

    def add(self, x: ValueDefinition):
        self._name_2_value[x.name] = x

    def contains(self, name: str) -> bool:
        return name in self._name_2_value

    @property
    def names_set(self) -> set:
        return set(self._name_2_value.keys())

    def lookup_file_ref(self, name: str) -> FileRef:
        """
        :raises KeyError: The symbol table does not contain name.
        """
        return self._name_2_value[name].file_ref


def empty_symbol_table() -> SymbolTable:
    return SymbolTable()


def singleton_symbol_table(element: ValueDefinition) -> SymbolTable:
    return SymbolTable({element.name: element})
