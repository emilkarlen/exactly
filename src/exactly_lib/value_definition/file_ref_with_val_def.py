import pathlib

from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.test_case_file_structure.file_ref import FileRef, FileRefWithPathSuffixBase
from exactly_lib.test_case_file_structure.path_part import PathPart
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.test_case_file_structure.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.value_definition.concrete_restrictions import FileRefRelativityRestriction
from exactly_lib.value_definition.concrete_values import FileRefValue
from exactly_lib.value_definition.value_structure import ValueReference, ValueContainer


def rel_value_definition(value_reference2: ValueReference, path_suffix: PathPart) -> FileRef:
    return _FileRefRelValueDefinition(path_suffix, value_reference2)


def value_ref2_of_path(val_def_name: str, accepted_relativities: PathRelativityVariants) -> ValueReference:
    return ValueReference(val_def_name, FileRefRelativityRestriction(accepted_relativities))


class _FileRefRelValueDefinition(FileRefWithPathSuffixBase):
    def __init__(self,
                 path_suffix: PathPart,
                 value_reference_of_path: ValueReference):
        super().__init__(path_suffix)
        self.value_reference_of_path = value_reference_of_path

    def value_references_of_paths(self) -> list:
        return [self.value_reference_of_path] + self._path_suffix.value_references

    def relativity(self, value_definitions: SymbolTable) -> RelOptionType:
        file_ref = self._lookup_file_ref(value_definitions)
        return file_ref.relativity(value_definitions)

    def exists_pre_sds(self, value_definitions: SymbolTable) -> bool:
        file_ref = self._lookup_file_ref(value_definitions)
        return file_ref.exists_pre_sds(value_definitions)

    def file_path_pre_sds(self, environment: PathResolvingEnvironmentPreSds) -> pathlib.Path:
        file_ref = self._lookup_file_ref(environment.value_definitions)
        return file_ref.file_path_pre_sds(environment) / self.path_suffix_path(environment.value_definitions)

    def file_path_post_sds(self, environment: PathResolvingEnvironmentPostSds) -> pathlib.Path:
        file_ref = self._lookup_file_ref(environment.value_definitions)
        return file_ref.file_path_post_sds(environment) / self.path_suffix_path(environment.value_definitions)

    def _lookup_file_ref(self, value_definitions: SymbolTable) -> FileRef:
        return lookup_file_ref_from_symbol_table(value_definitions, self.value_reference_of_path.name)


def lookup_file_ref_from_symbol_table(value_definitions: SymbolTable, name: str) -> FileRef:
    value_container = value_definitions.lookup(name)
    assert isinstance(value_container, ValueContainer), 'Value in SymTbl must be ValueContainer'
    value = value_container.value
    assert isinstance(value, FileRefValue), 'Referenced definition must be FileRefValue'
    return value.file_ref
