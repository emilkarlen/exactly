from typing import Sequence

from exactly_lib.symbol import lookups
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver, PathPartResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.util.symbol_table import SymbolTable


class FileRefResolverRelSymbol(FileRefResolver):
    def __init__(self,
                 path_suffix: PathPartResolver,
                 symbol_reference_of_path: SymbolReference):
        self.path_suffix = path_suffix
        self.symbol_reference_of_path = symbol_reference_of_path

    def resolve(self, symbols: SymbolTable) -> FileRef:
        base_file_ref = lookups.lookup_and_resolve_file_ref(symbols, self.symbol_reference_of_path.name)
        return file_refs.stacked(base_file_ref, self.path_suffix.resolve(symbols))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return [self.symbol_reference_of_path] + list(self.path_suffix.references)
