from exactly_lib.named_element.resolver_structure import FileSelectorResolver
from exactly_lib.type_system_values.file_selector import FileSelector
from exactly_lib.util.dir_contents_selection import Selectors
from exactly_lib.util.symbol_table import SymbolTable


class FileSelectorResolverConstantTestImpl(FileSelectorResolver):
    def __init__(self, resolved_value: FileSelector,
                 references: list):
        self._references = references
        self._resolved_value = resolved_value

    @property
    def resolved_value(self) -> FileSelector:
        return self._resolved_value

    @property
    def references(self) -> list:
        return self._references

    def resolve(self, named_elements: SymbolTable) -> FileSelector:
        return self._resolved_value


def fake(selectors: Selectors = Selectors(),
         references: list = None) -> FileSelectorResolverConstantTestImpl:
    return FileSelectorResolverConstantTestImpl(FileSelector(selectors),
                                                references if references else [])
