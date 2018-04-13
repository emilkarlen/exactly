import pathlib
from typing import Sequence

from exactly_lib.symbol import lookups
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver, PathPartResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import SpecificPathRelativity
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.concrete_path_parts import PathPartAsNothing
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.data.path_part import PathPart
from exactly_lib.util.symbol_table import SymbolTable


class FileRefResolverRelSymbol(FileRefResolver):
    def __init__(self,
                 path_suffix: PathPartResolver,
                 symbol_reference_of_path: SymbolReference):
        self.path_suffix = path_suffix
        self.symbol_reference_of_path = symbol_reference_of_path

    def resolve(self, symbols: SymbolTable) -> FileRef:
        base_file_ref = lookups.lookup_and_resolve_file_ref(symbols, self.symbol_reference_of_path.name)
        return StackedFileRef(base_file_ref, self.path_suffix.resolve(symbols))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return [self.symbol_reference_of_path] + self.path_suffix.references


class StackedFileRef(FileRef):
    def __init__(self, base_file_ref: FileRef, path_suffix: PathPart):
        self._stacked_path_suffix = path_suffix
        self._combined_path_suffix = _combine(base_file_ref.path_suffix(), path_suffix)
        self.base_file_ref = base_file_ref

    def relativity(self) -> SpecificPathRelativity:
        return self.base_file_ref.relativity()

    def path_suffix(self) -> PathPart:
        return self._combined_path_suffix

    def path_suffix_str(self) -> str:
        return self._combined_path_suffix.value()

    def path_suffix_path(self) -> pathlib.Path:
        return pathlib.Path(self.path_suffix_str())

    def _stacked_path_suffix_path(self) -> pathlib.Path:
        return pathlib.Path(self._stacked_path_suffix.value())

    def has_dir_dependency(self) -> bool:
        return self.base_file_ref.has_dir_dependency()

    def value_when_no_dir_dependencies(self) -> pathlib.Path:
        return self.base_file_ref.value_when_no_dir_dependencies() / self._stacked_path_suffix_path()

    def value_pre_sds(self, hds: HomeDirectoryStructure) -> pathlib.Path:
        return self.base_file_ref.value_pre_sds(hds) / self._stacked_path_suffix_path()

    def value_post_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self.base_file_ref.value_post_sds(sds) / self._stacked_path_suffix_path()


def _combine(first: PathPart, second: PathPart) -> PathPart:
    if isinstance(first, PathPartAsNothing):
        return second
    if isinstance(second, PathPartAsNothing):
        return first
    p = pathlib.Path(first.value()) / pathlib.Path(second.value())
    return file_refs.constant_path_part(str(p))
