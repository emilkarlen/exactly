import pathlib

from exactly_lib.test_case.file_ref_relativity import RelOptionType
from exactly_lib.test_case.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds, PathResolvingEnvironmentPreOrPostSds
from exactly_lib.util.symbol_table import SymbolTable


class FileRef:
    """
    A reference to a file (any kind of file), with functionality to resolve it's path,
    and information about whether it exists pre SDS or not.
    """

    def __init__(self, file_name: str):
        self._file_name = file_name

    @property
    def file_name(self) -> str:
        return self._file_name

    def value_references_of_paths(self) -> list:
        """
        All `ValueReferenceOfPath`s that are _directly_ used by this object.
        I.e, if value <name> is referenced, that in turn references <name2>,
        then <name2> should not be included in the result because of this
        reason.
        :rtype [`ValueReferenceOfPath`]
        """
        raise NotImplementedError()

    def exists_pre_sds(self, value_definitions: SymbolTable) -> bool:
        raise NotImplementedError()

    def relativity(self, value_definitions: SymbolTable) -> RelOptionType:
        # TODO [val-def] Return value should be able to denote absolute/no relativity
        raise NotImplementedError()

    def file_path_pre_sds(self, environment: PathResolvingEnvironmentPreSds) -> pathlib.Path:
        """
        :raises ValueError: This file exists only post-SDS.
        """
        raise NotImplementedError()

    def file_path_post_sds(self, environment: PathResolvingEnvironmentPostSds) -> pathlib.Path:
        """
        :raises ValueError: This file exists pre-SDS.
        """
        raise NotImplementedError()

    def file_path_pre_or_post_sds(self, environment: PathResolvingEnvironmentPreOrPostSds) -> pathlib.Path:
        if self.exists_pre_sds(environment.value_definitions):
            return self.file_path_pre_sds(environment)
        else:
            return self.file_path_post_sds(environment)
