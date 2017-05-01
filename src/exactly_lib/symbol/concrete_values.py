from enum import Enum

from exactly_lib.symbol.value_structure import Value
from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.util.symbol_table import SymbolTable


class ValueType(Enum):
    STRING = 0
    PATH = 1


class SymbolValueResolver(Value):
    """
    Base class for values in the symbol table used by Exactly.
    """

    @property
    def value_type(self) -> ValueType:
        raise NotImplementedError()

    @property
    def references(self) -> list:
        """Values in the symbol table used by this object."""
        raise NotImplementedError()

    def resolve(self, symbols: SymbolTable):
        """
        Resolves the value given a symbol table.
        :rtype: Depends on the concrete value.
        """
        raise NotImplementedError()


class StringResolver(SymbolValueResolver):
    @property
    def value_type(self) -> ValueType:
        return ValueType.STRING

    def resolve(self, symbols: SymbolTable) -> str:
        raise NotImplementedError()

    @property
    def references(self) -> list:
        raise NotImplementedError()

    def __str__(self):
        return str(type(self))


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
