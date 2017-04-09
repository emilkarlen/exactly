from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.value_definition.value_structure import Value


class SymbolValue(Value):
    """
    TODO Improve name, description
    """

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


class StringValue(SymbolValue):
    def __init__(self, string: str):
        self._string = string

    def resolve(self, symbols: SymbolTable) -> str:
        return self._string

    @property
    def string(self) -> str:
        return self._string

    @property
    def references(self) -> list:
        return []

    def __str__(self):
        return str(type(self)) + '\'' + self._string + '\''


class FileRefValue(SymbolValue):
    def __init__(self, file_ref: FileRef):
        self._file_ref = file_ref

    def resolve(self, symbols: SymbolTable) -> FileRef:
        return self._file_ref

    @property
    def file_ref(self) -> FileRef:
        return self._file_ref

    @property
    def references(self) -> list:
        return self._file_ref.value_references()

    def __str__(self):
        return str(type(self)) + '\'' + str(self._file_ref) + '\''


class ValueVisitor:
    """
    Visitor of `Value`
    """

    def visit(self, value: Value):
        """
        :return: Return value from _visit... method
        """
        if isinstance(value, FileRefValue):
            return self._visit_file_ref(value)
        if isinstance(value, StringValue):
            return self._visit_string(value)
        raise TypeError('Unknown {}: {}'.format(Value, str(value)))

    def _visit_string(self, value: StringValue):
        raise NotImplementedError()

    def _visit_file_ref(self, value: FileRefValue):
        raise NotImplementedError()
