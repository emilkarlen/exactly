from typing import Sequence

from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.data.file_ref import FileRef
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
    def references(self) -> Sequence[SymbolReference]:
        return ()

    def __str__(self):
        return str(type(self)) + '\'' + str(self._file_ref) + '\''
