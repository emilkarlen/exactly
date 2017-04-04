import pathlib

from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.test_case_file_structure.path_part import PathPart
from exactly_lib.test_case_file_structure.path_relativity import SpecificPathRelativity, specific_relative_relativity, \
    RelOptionType
from exactly_lib.util.symbol_table import SymbolTable


class FileRefWithPathSuffixBase(FileRef):
    def __init__(self, path_part: PathPart):
        self._path_suffix = path_part

    def path_suffix(self, symbols: SymbolTable) -> PathPart:
        return self._path_suffix

    def path_suffix_str(self, symbols: SymbolTable) -> str:
        return self._path_suffix.resolve(symbols)

    def path_suffix_path(self, symbols: SymbolTable) -> pathlib.Path:
        return pathlib.Path(self.path_suffix_str(symbols))


class FileRefWithPathSuffixAndIsNotAbsoluteBase(FileRefWithPathSuffixBase):
    def __init__(self, path_part: PathPart):
        super().__init__(path_part)

    def specific_relativity(self, value_definitions: SymbolTable) -> SpecificPathRelativity:
        rel_option_type = self._relativity(value_definitions)
        return specific_relative_relativity(rel_option_type)

    def _relativity(self, value_definitions: SymbolTable) -> RelOptionType:
        raise NotImplementedError()