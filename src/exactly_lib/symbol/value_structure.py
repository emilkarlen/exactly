from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.type_system_values.value_type import ValueType
from exactly_lib.util.line_source import Line
from exactly_lib.util.symbol_table import SymbolTableValue, SymbolTable


class SymbolValueResolver:
    """
    Base class for values in the symbol table used by Exactly.
    """

    @property
    def value_type(self) -> ValueType:
        raise NotImplementedError()

    @property
    def references(self) -> list:
        """
        All :class:`SymbolReference` directly referenced by this object.

        :type: [`SymbolReference`]
        """
        raise NotImplementedError()

    def resolve(self, symbols: SymbolTable) -> DirDependentValue:
        """
        Resolves the value given a symbol table.
        :rtype: Depends on the concrete value.
        """
        raise NotImplementedError()


class ValueContainer(SymbolTableValue):
    """
    The info about a value that is stored in a symbol table.

    A value together with meta info
    """

    def __init__(self, source: Line, value: SymbolValueResolver):
        self._source = source
        self._value = value

    @property
    def definition_source(self) -> Line:
        """The source code of the definition of the value."""
        return self._source

    @property
    def value(self) -> SymbolValueResolver:
        return self._value
