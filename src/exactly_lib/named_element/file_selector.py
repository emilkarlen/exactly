from exactly_lib.named_element.resolver_structure import FileSelectorResolver
from exactly_lib.type_system_values.file_selector import FileSelector
from exactly_lib.util.symbol_table import SymbolTable


class FileSelectorConstant(FileSelectorResolver):
    """
    A :class:`FileSelectorResolver` that is a constant :class:`FileSelector`
    """

    def __init__(self, file_selector: FileSelector):
        self._file_ref = file_selector

    def resolve(self, symbols: SymbolTable) -> FileSelector:
        return self._file_ref

    @property
    def references(self) -> list:
        return []

    def __str__(self):
        return str(type(self)) + '\'' + str(self._file_ref) + '\''
