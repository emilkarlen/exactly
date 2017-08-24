from exactly_lib.named_element.resolver_structure import FileSelectorResolver
from exactly_lib.type_system_values.file_selector import FileSelector
from exactly_lib.util.dir_contents_selection import Selectors
from exactly_lib.util.symbol_table import SymbolTable


def constant(selectors: Selectors = Selectors()) -> FileSelectorResolver:
    return _FileSelectorResolverConstantTestImpl(FileSelector(selectors))


class _FileSelectorResolverConstantTestImpl(FileSelectorResolver):
    def __init__(self, resolved_value: FileSelector):
        self.resolved_value = resolved_value

    @property
    def references(self) -> list:
        return []

    def resolve(self, named_elements: SymbolTable) -> FileSelector:
        return self.resolved_value
