import pathlib

from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.test_case_file_structure.file_ref_relativity import RelOptionType
from exactly_lib.test_case_file_structure.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.value_definition.symbol_table_contents import FileRefValue
from exactly_lib.value_definition.value_definition_usage import ValueReferenceOfPath


def rel_value_definition(value_reference_of_path: ValueReferenceOfPath, file_name: str) -> FileRef:
    return _FileRefRelValueDefinition(file_name, value_reference_of_path)


class _FileRefRelValueDefinition(FileRef):
    def __init__(self,
                 file_name: str,
                 value_reference_of_path: ValueReferenceOfPath):
        super().__init__(file_name)
        self.value_reference_of_path = value_reference_of_path

    def value_references_of_paths(self) -> list:
        return [self.value_reference_of_path]

    def relativity(self, value_definitions: SymbolTable) -> RelOptionType:
        file_ref = self._lookup_file_ref(value_definitions)
        return file_ref.relativity(value_definitions)

    def exists_pre_sds(self, value_definitions: SymbolTable) -> bool:
        file_ref = self._lookup_file_ref(value_definitions)
        return file_ref.exists_pre_sds(value_definitions)

    def file_path_pre_sds(self, environment: PathResolvingEnvironmentPreSds) -> pathlib.Path:
        file_ref = self._lookup_file_ref(environment.value_definitions)
        return file_ref.file_path_pre_sds(environment) / self.file_name

    def file_path_post_sds(self, environment: PathResolvingEnvironmentPostSds) -> pathlib.Path:
        file_ref = self._lookup_file_ref(environment.value_definitions)
        return file_ref.file_path_post_sds(environment) / self.file_name

    def _lookup_file_ref(self, value_definitions: SymbolTable) -> FileRef:
        return lookup_file_ref_from_symbol_table(value_definitions, self.value_reference_of_path.name)


def lookup_file_ref_from_symbol_table(value_definitions: SymbolTable, name: str) -> FileRef:
    value = value_definitions.lookup(name)
    assert isinstance(value, FileRefValue), 'Referenced definition must be FileRefValue'
    return value.file_ref
