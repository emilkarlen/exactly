from exactly_lib.symbol.string_resolver import StringResolver
from exactly_lib.symbol.value_structure import Value, SymbolValueResolver
from exactly_lib.type_system_values.file_ref import FileRef
from exactly_lib.type_system_values.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable


class FileRefResolver(SymbolValueResolver):
    @property
    def value_type(self) -> ValueType:
        return ValueType.PATH

    def resolve(self, symbols: SymbolTable) -> FileRef:
        raise NotImplementedError()

    @property
    def references(self) -> list:
        raise NotImplementedError()

    def __str__(self):
        return str(type(self))


class ValueVisitor:
    """
    Visitor of `Value`
    """

    def visit(self, value: Value):
        """
        :return: Return value from _visit... method
        """
        if isinstance(value, FileRefResolver):
            return self._visit_file_ref(value)
        if isinstance(value, StringResolver):
            return self._visit_string(value)
        raise TypeError('Unknown {}: {}'.format(Value, str(value)))

    def _visit_string(self, value: StringResolver):
        raise NotImplementedError()

    def _visit_file_ref(self, value: FileRefResolver):
        raise NotImplementedError()
