from exactly_lib.util.line_source import Line
from exactly_lib.util.symbol_table import SymbolTableValue, SymbolTable


class Value:
    """
    A value of a type that the type system supports
    """
    pass


class ValueRestriction:
    """
    A restriction on a value that can be checked "statically" -
    i.e. does not check actual resolved value.
    """

    def is_satisfied_by(self, symbol_table: SymbolTable, value: Value) -> str:
        """
        :return: None if satisfied, otherwise an error message
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
    def source(self) -> Line:
        return self._source

    @property
    def value(self) -> Value:
        return self._value


class ValueUsage2:
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name


class ValueDefinition2(ValueUsage2):
    def __init__(self,
                 name: str,
                 value_container: ValueContainer):
        super().__init__(name)
        self._value_container = value_container

    @property
    def value_container(self) -> ValueContainer:
        return self._value_container


class ValueReference2(ValueUsage2):
    def __init__(self,
                 name: str,
                 value_restriction: ValueRestriction):
        super().__init__(name)
        self._value_restriction = value_restriction

    @property
    def value_restriction(self) -> ValueRestriction:
        return self._value_restriction


class ValueUsageVisitor:
    """
    Visitor of `Value`
    """

    def visit(self, value_usage: ValueUsage2):
        """
        :return: Return value from _visit... method
        """
        if isinstance(value_usage, ValueDefinition2):
            return self._visit_definition(value_usage)
        if isinstance(value_usage, ValueReference2):
            return self._visit_reference(value_usage)
        raise TypeError('Unknown {}: {}'.format(Value, str(value_usage)))

    def _visit_definition(self, value_usage: ValueDefinition2):
        raise NotImplementedError()

    def _visit_reference(self, value_usage: ValueReference2):
        raise NotImplementedError()
