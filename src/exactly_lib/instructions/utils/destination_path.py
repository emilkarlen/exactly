import pathlib

from exactly_lib.instructions.utils.arg_parse.relative_path_options import REL_OPTIONS_MAP
from exactly_lib.test_case.file_ref import FileRef
from exactly_lib.test_case.file_ref_relativity import RelOptionType
from exactly_lib.test_case.file_refs import lookup_file_ref_from_symbol_table
from exactly_lib.test_case.path_resolving_environment import PathResolvingEnvironmentPostSds, \
    PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case.value_definition import ValueReferenceOfPath
from exactly_lib.util.symbol_table import SymbolTable


class DestinationPath:
    def destination_type(self, value_definitions: SymbolTable) -> RelOptionType:
        raise NotImplementedError()

    def value_references_of_paths(self, ) -> list:
        """
        All `ValueReferenceOfPath`s that are _directly_ used by this object.
        I.e, if value <name> is referenced, that in turn references <name2>,
        then <name2> should not be included in the result because of this
        reason.
        :rtype [`ValueReferenceOfPath`]
        """
        raise NotImplementedError()

    @property
    def path_argument(self) -> pathlib.PurePath:
        raise NotImplementedError()

    def root_path(self, environment: PathResolvingEnvironmentPreOrPostSds) -> pathlib.Path:
        raise NotImplementedError()

    def resolved_path(self, environment: PathResolvingEnvironmentPreOrPostSds) -> pathlib.Path:
        raise NotImplementedError()

    def resolved_path_if_not_rel_home(self, environment: PathResolvingEnvironmentPostSds) -> pathlib.Path:
        raise NotImplementedError()


class _DestinationPathFromRelRootResolver(DestinationPath):
    def __init__(self,
                 destination_type: RelOptionType,
                 path_argument: pathlib.PurePath):
        self._root_resolver = REL_OPTIONS_MAP[destination_type].root_resolver
        self._path_argument = path_argument

    def destination_type(self, value_definitions: SymbolTable) -> RelOptionType:
        return self._root_resolver.relativity_type

    def value_references_of_paths(self) -> list:
        return []

    @property
    def path_argument(self) -> pathlib.PurePath:
        return self._path_argument

    def root_path(self, environment: PathResolvingEnvironmentPreOrPostSds) -> pathlib.Path:
        return self._root_resolver.from_home_and_sds(environment.home_and_sds)

    def resolved_path(self, environment: PathResolvingEnvironmentPreOrPostSds) -> pathlib.Path:
        return self.root_path(environment) / self.path_argument

    def resolved_path_if_not_rel_home(self, environment: PathResolvingEnvironmentPostSds) -> pathlib.Path:
        return self._root_resolver.from_non_home(environment.sds) / self.path_argument


class _DestinationPathBasedOnValueDefinition(DestinationPath):
    def __init__(self,
                 value_definition_reference: ValueReferenceOfPath,
                 path_argument: pathlib.PurePath):
        self._value_definition_reference = value_definition_reference
        self._path_argument = path_argument

    def destination_type(self, value_definitions: SymbolTable) -> RelOptionType:
        raise NotImplementedError()

    def value_references_of_paths(self) -> list:
        return [self._value_definition_reference]

    @property
    def path_argument(self) -> pathlib.PurePath:
        return self._path_argument

    def root_path(self, environment: PathResolvingEnvironmentPreOrPostSds) -> pathlib.Path:
        file_ref = self._lookup_file_ref(environment.value_definitions)
        return file_ref.file_path_pre_or_post_sds(environment)

    def resolved_path(self, environment: PathResolvingEnvironmentPreOrPostSds) -> pathlib.Path:
        return self.root_path(environment) / self.path_argument

    def resolved_path_if_not_rel_home(self, environment: PathResolvingEnvironmentPostSds) -> pathlib.Path:
        file_ref = self._lookup_file_ref(environment.value_definitions)
        root_path = file_ref.file_path_post_sds(environment)
        return root_path / self.path_argument

    def _lookup_file_ref(self, value_definitions: SymbolTable) -> FileRef:
        return lookup_file_ref_from_symbol_table(value_definitions, self._value_definition_reference.name)


def from_rel_option(destination_type: RelOptionType,
                    path_argument: pathlib.PurePath) -> DestinationPath:
    return _DestinationPathFromRelRootResolver(destination_type, path_argument)


def from_value_definition(value_definition_reference: ValueReferenceOfPath,
                          path_argument: pathlib.PurePath) -> DestinationPath:
    return _DestinationPathBasedOnValueDefinition(value_definition_reference, path_argument)
