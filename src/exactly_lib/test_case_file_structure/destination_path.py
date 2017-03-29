import pathlib

from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_file_structure.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds, \
    PathResolvingEnvironmentPostSds
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
