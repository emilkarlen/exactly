from exactly_lib.test_case.file_ref import FileRef
from exactly_lib.util.line_source import Line
from exactly_lib.util.symbol_table import SymbolTableValue


class FileRefValue(SymbolTableValue):
    def __init__(self, source: Line, file_ref: FileRef):
        self._source = source
        self._file_ref = file_ref

    @property
    def source(self) -> Line:
        return self._source

    @property
    def file_ref(self) -> FileRef:
        return self._file_ref
