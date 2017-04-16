import pathlib

from exactly_lib.test_case_file_structure.path_part import PathPart
from exactly_lib.test_case_file_structure.path_relativity import SpecificPathRelativity
from exactly_lib.test_case_file_structure.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds, PathResolvingEnvironmentPreOrPostSds
from exactly_lib.util.symbol_table import SymbolTable


class FileRef:
    """
    A reference to a file (any kind of file), with functionality to resolve it's path,
    and information about whether it exists pre SDS or not.
    """

    def path_suffix(self) -> PathPart:
        raise NotImplementedError()

    def path_suffix_str(self) -> str:
        raise NotImplementedError()

    def path_suffix_path(self) -> pathlib.Path:
        raise NotImplementedError()

    def exists_pre_sds(self, value_definitions: SymbolTable) -> bool:
        raise NotImplementedError()

    def relativity(self, value_definitions: SymbolTable) -> SpecificPathRelativity:
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
