from typing import Sequence, Tuple, Optional

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.test_case_utils.files_condition.structure import FilesConditionSdv, FilesConditionDdv
from exactly_lib.type_val_deps.sym_ref import restrictions, symbol_lookup
from exactly_lib.type_val_deps.types.file_matcher import FileMatcherDdv, FileMatcherSdv
from exactly_lib.type_val_deps.types.string.string_ddv import StringDdv
from exactly_lib.type_val_deps.types.string.string_sdv import StringSdv
from exactly_lib.util.functional import map_optional
from exactly_lib.util.symbol_table import SymbolTable


def new_constant(files: Sequence[Tuple[StringSdv, Optional[FileMatcherSdv]]]) -> FilesConditionSdv:
    return _ConstantSdv(files)


def new_empty() -> FilesConditionSdv:
    return _ConstantSdv(())


def new_reference(symbol_name: str) -> FilesConditionSdv:
    return _ReferenceSdv(symbol_name)


class _ConstantSdv(FilesConditionSdv):
    def __init__(self, files: Sequence[Tuple[StringSdv, Optional[FileMatcherSdv]]]):
        self._files = files
        self._references = []
        for file_name, mb_matcher in files:
            self._references += file_name.references
            if mb_matcher:
                self._references += mb_matcher.references

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> FilesConditionDdv:

        def resolve_matcher(x: FileMatcherSdv) -> FileMatcherDdv:
            return x.resolve(symbols)

        def resolve_entry(file_name: StringSdv, matcher: Optional[FileMatcherSdv]
                          ) -> Tuple[StringDdv, Optional[FileMatcherDdv]]:
            return file_name.resolve(symbols), map_optional(resolve_matcher, matcher)

        return FilesConditionDdv([
            resolve_entry(fn, mb_matcher)
            for fn, mb_matcher in self._files
        ])


class _ReferenceSdv(FilesConditionSdv):
    def __init__(self, symbol_name: str):
        self._symbol_name = symbol_name
        self._references = (
            SymbolReference(symbol_name,
                            restrictions.ValueTypeRestriction(ValueType.FILES_CONDITION)),
        )

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> FilesConditionDdv:
        referenced_sdv = symbol_lookup.lookup_files_condition(symbols, self._symbol_name)
        return referenced_sdv.resolve(symbols)
