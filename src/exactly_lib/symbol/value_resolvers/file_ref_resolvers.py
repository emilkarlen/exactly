from exactly_lib.symbol.concrete_resolvers import FileRefResolver
from exactly_lib.type_system_values.file_ref import FileRef
from exactly_lib.util.symbol_table import SymbolTable


class FileRefConstant(FileRefResolver):
    """
    A `FileRefResolver` that is a constant `FileRef`
    """

    def __init__(self, file_ref: FileRef):
        self._file_ref = file_ref

    def resolve(self, symbols: SymbolTable) -> FileRef:
        return self._file_ref

    @property
    def references(self) -> list:
        return []

    def __str__(self):
        return str(type(self)) + '\'' + str(self._file_ref) + '\''
