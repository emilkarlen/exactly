from exactly_lib.util.line_source import Line
from exactly_lib.util.symbol_table import SymbolTableValue, SymbolTable, Entry


class Value:
    """
    A value of a type that the type system supports
    """

    @property
    def references(self) -> list:
        """All `ValueReference` directly referenced by this object"""
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
    A restriction on a value that can be checked "statically" -
    i.e. does not check actual resolved value.
    """

    def is_satisfied_by(self, symbol_table: SymbolTable, symbol_name: str, value: ValueContainer) -> str:
        """
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
