import pathlib

from exactly_lib.symbol.concrete_restrictions import FileRefRelativityRestriction
from exactly_lib.symbol.concrete_values import FileRefResolver
from exactly_lib.symbol.value_resolvers.path_part_resolver import PathPartResolver
from exactly_lib.symbol.value_structure import SymbolReference, ValueContainer
from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.test_case_file_structure.path_part import PathPart
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, \
    SpecificPathRelativity
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.symbol_table import SymbolTable


def rel_symbol(symbol_reference2: SymbolReference, path_suffix: PathPartResolver) -> FileRefResolver:
    return _FileRefResolverRelSymbol(path_suffix, symbol_reference2)


def value_ref2_of_path(symbol_name: str, accepted_relativities: PathRelativityVariants) -> SymbolReference:
    return SymbolReference(symbol_name, FileRefRelativityRestriction(accepted_relativities))


class _FileRefResolverRelSymbol(FileRefResolver):
    def __init__(self,
                 path_suffix: PathPartResolver,
                 symbol_reference_of_path: SymbolReference):
        self.path_suffix = path_suffix
        self.symbol_reference_of_path = symbol_reference_of_path

    def resolve(self, symbols: SymbolTable) -> FileRef:
        base_file_ref = lookup_file_ref_from_symbol_table(symbols, self.symbol_reference_of_path.name)
        return _StackedFileRef(base_file_ref, self.path_suffix.resolve(symbols))

    @property
    def references(self) -> list:
        return [self.symbol_reference_of_path] + self.path_suffix.references


class _StackedFileRef(FileRef):
    def __init__(self, base_file_ref: FileRef, path_suffix: PathPart):
        self._path_suffix = path_suffix
        self.base_file_ref = base_file_ref

    def relativity(self) -> SpecificPathRelativity:
        return self.base_file_ref.relativity()

    def path_suffix(self) -> PathPart:
        return self._path_suffix

    def path_suffix_str(self) -> str:
        return self._path_suffix.resolve()

    def path_suffix_path(self) -> pathlib.Path:
        return pathlib.Path(self.path_suffix_str())

    def exists_pre_sds(self) -> bool:
        return self.base_file_ref.exists_pre_sds()

    def value_pre_sds(self, home_dir_path: pathlib.Path) -> pathlib.Path:
        return self.base_file_ref.value_pre_sds(home_dir_path) / self.path_suffix_path()

    def value_post_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self.base_file_ref.value_post_sds(sds) / self.path_suffix_path()


def lookup_file_ref_from_symbol_table(symbols: SymbolTable, name: str) -> FileRef:
    value_container = symbols.lookup(name)
    assert isinstance(value_container, ValueContainer), 'Value in SymTbl must be ValueContainer'
    value = value_container.value
    assert isinstance(value, FileRefResolver), 'Referenced symbol must be FileRefResolver'
    return value.resolve(symbols)
