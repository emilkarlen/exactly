from typing import Sequence

from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.util.symbol_table import SymbolTable


def arbitrary_resolver() -> FileRefResolver:
    return FileRefResolverTestImplWithConstantFileRefAndSymbolReferences(
        file_refs.simple_of_rel_option(RelOptionType.REL_ACT, 'base-name'),
        (),
    )


class FileRefResolverTestImplWithConstantFileRefAndSymbolReferences(FileRefResolver):
    def __init__(self,
                 file_ref: FileRef,
                 references: Sequence[SymbolReference]):
        self._file_ref = file_ref
        self._references = references

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> FileRef:
        return self._file_ref
