from exactly_lib.test_case.file_ref import FileRef
from exactly_lib.util import symbol_table
from exactly_lib.util.line_source import Line
from exactly_lib.util.symbol_table import Value


class FileRefValue(Value):
    def __init__(self, source: Line, file_ref: FileRef):
        self._source = source
        self._file_ref = file_ref

    @property
    def source(self) -> Line:
        return self._source

    @property
    def file_ref(self) -> FileRef:
        return self._file_ref


class ValueUsage(object):
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name


class ValueReference(ValueUsage):
    pass


class ValueDefinition(ValueUsage):
    def __init__(self, name: str):
        super().__init__(name)

    @property
    def symbol_table_entry(self) -> symbol_table.Entry:
        return symbol_table.Entry(self.name, symbol_table.Value())
