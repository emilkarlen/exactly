from enum import Enum

from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.util.line_source import Line
from exactly_lib.util.symbol_table import SymbolTableValue, SymbolTable, Entry


class ValueType(Enum):
    STRING = 0
    PATH = 1


class Value:
    """
    A value of a type that the type system supports
    """

    @property
    def references(self) -> list:
        """All `ValueReference` directly referenced by this object"""
        raise NotImplementedError()


class SymbolValueResolver(Value):
    """
    Base class for values in the symbol table used by Exactly.
    """

    @property
    def value_type(self) -> ValueType:
        raise NotImplementedError()

    @property
    def references(self) -> list:
        """
        Values in the symbol table used by this object.

        :type: [SymbolReference]
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

    def __init__(self, source: Line, value: Value):
        self._source = source
        self._value = value

    @property
    def definition_source(self) -> Line:
        """The source code of the definition of the value."""
        return self._source

    @property
    def value(self) -> Value:
        return self._value


class ValueRestriction:
    """
    A restriction on a value in the symbol table, that is applied by the frame work - 
    i.e. not by specific instructions.
    """

    def is_satisfied_by(self, symbol_table: SymbolTable, symbol_name: str, value: ValueContainer) -> str:
        """
        :param symbol_table: A symbol table that contains all symbols that the checked value refer to.
        :param symbol_name: The name of the symbol that the restriction applies to
        :param value: The value that the restriction applies to
        :return: None if satisfied, otherwise an error message
        """
        raise NotImplementedError()


class SymbolUsage:
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name


class SymbolDefinition(SymbolUsage):
    """
    Defines a symbol so that it can be used via references to it.
    """

    def __init__(self,
                 name: str,
                 value_container: ValueContainer):
        super().__init__(name)
        self._value_container = value_container

    @property
    def value_container(self) -> ValueContainer:
        return self._value_container

    @property
    def references(self) -> list:
        """All `ValueReference` directly referenced by this object"""
        return self._value_container.value.references

    @property
    def symbol_table_entry(self) -> Entry:
        return Entry(self.name, self.value_container)


class SymbolReference(SymbolUsage):
    """
    A reference to a symbol that is assumed to have been previously defined.
    """

    def __init__(self,
                 name: str,
                 value_restriction: ValueRestriction):
        super().__init__(name)
        self._value_restriction = value_restriction

    @property
    def value_restriction(self) -> ValueRestriction:
        return self._value_restriction


class SymbolUsageVisitor:
    """
    Visitor of `SymbolUsage`
    """

    def visit(self, symbol_usage: SymbolUsage):
        """
        :return: Return value from _visit... method
        """
        if isinstance(symbol_usage, SymbolDefinition):
            return self._visit_definition(symbol_usage)
        if isinstance(symbol_usage, SymbolReference):
            return self._visit_reference(symbol_usage)
        raise TypeError('Unknown {}: {}'.format(Value, str(symbol_usage)))

    def _visit_definition(self, symbol_usage: SymbolDefinition):
        raise NotImplementedError()

    def _visit_reference(self, symbol_usage: SymbolReference):
        raise NotImplementedError()
