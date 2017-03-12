import pathlib

from exactly_lib.instructions.utils.arg_parse.relative_path_options import REL_OPTIONS_MAP
from exactly_lib.instructions.utils.relativity_root import RelOptionType
from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.test_case.value_definition import ValueReferenceOfPath


class DestinationPath:
    @property
    def destination_type(self) -> RelOptionType:
        raise NotImplementedError()

    def value_references_of_paths(self) -> list:
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

    def root_path(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        raise NotImplementedError()

    def resolved_path(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        raise NotImplementedError()

    def resolved_path_if_not_rel_home(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()


class _DestinationPathFromRelRootResolver(DestinationPath):
    def __init__(self,
                 destination_type: RelOptionType,
                 path_argument: pathlib.PurePath):
        self._root_resolver = REL_OPTIONS_MAP[destination_type].root_resolver
        self._path_argument = path_argument

    @property
    def destination_type(self) -> RelOptionType:
        return self._root_resolver.relativity_type

    def value_references_of_paths(self) -> list:
        return []

    @property
    def path_argument(self) -> pathlib.PurePath:
        return self._path_argument

    def root_path(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        return self._root_resolver.from_home_and_sds(home_and_sds)

    def resolved_path(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        return self.root_path(home_and_sds) / self.path_argument

    def resolved_path_if_not_rel_home(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self._root_resolver.from_non_home(sds) / self.path_argument


class _DestinationPathBasedOnValueDefinition(DestinationPath):
    def __init__(self,
                 value_definition_reference: ValueReferenceOfPath,
                 path_argument: pathlib.PurePath):
        self._value_definition_reference = value_definition_reference
        self._path_argument = path_argument

    @property
    def destination_type(self) -> RelOptionType:
        raise NotImplementedError()

    def value_references_of_paths(self) -> list:
        return [self._value_definition_reference]

    @property
    def path_argument(self) -> pathlib.PurePath:
        return self._path_argument

    def root_path(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        raise NotImplementedError()

    def resolved_path(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        raise NotImplementedError()

    def resolved_path_if_not_rel_home(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()


def from_rel_option(destination_type: RelOptionType,
                    path_argument: pathlib.PurePath) -> DestinationPath:
    return _DestinationPathFromRelRootResolver(destination_type, path_argument)


def from_value_definition(value_definition_reference: ValueReferenceOfPath,
                          path_argument: pathlib.PurePath) -> DestinationPath:
    return _DestinationPathBasedOnValueDefinition(value_definition_reference, path_argument)
