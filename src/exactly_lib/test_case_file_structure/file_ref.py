import pathlib

from exactly_lib.test_case_file_structure.path_part import PathPart
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, SpecificPathRelativity, \
    specific_relative_relativity
from exactly_lib.test_case_file_structure.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds, PathResolvingEnvironmentPreOrPostSds
from exactly_lib.util.symbol_table import SymbolTable


class FileRef:
    """
    A reference to a file (any kind of file), with functionality to resolve it's path,
    and information about whether it exists pre SDS or not.
    """

    def path_suffix(self, symbols: SymbolTable) -> PathPart:
        raise NotImplementedError()

    def path_suffix_str(self, symbols: SymbolTable) -> str:
        raise NotImplementedError()

    def path_suffix_path(self, symbols: SymbolTable) -> pathlib.Path:
        raise NotImplementedError()

    def value_references_of_paths(self) -> list:
        """
        All `ValueReference`s that are _directly_ used by this object.
        I.e, if value <name> is referenced, that in turn references <name2>,
        then <name2> should not be included in the result because of this
        reason.
        :rtype [`ValueReference`]
        """
        raise NotImplementedError()

    def exists_pre_sds(self, value_definitions: SymbolTable) -> bool:
        raise NotImplementedError()

    def specific_relativity(self, value_definitions: SymbolTable) -> SpecificPathRelativity:
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
