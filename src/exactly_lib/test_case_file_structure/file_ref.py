import pathlib

from exactly_lib.test_case_file_structure.file_ref_relativity import RelOptionType, SpecificPathRelativity, \
    specific_relative_relativity
from exactly_lib.test_case_file_structure.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds, PathResolvingEnvironmentPreOrPostSds
from exactly_lib.util.symbol_table import SymbolTable


class PathSuffix:
    """
    The relative path that follows the root path of the `FileRef`.
    """

    def resolve(self, symbols: SymbolTable) -> str:
        raise NotImplementedError()

    @property
    def value_references(self) -> list:
        """
        :rtype: [ValueReference]
        """
        raise NotImplementedError()


class PathSuffixAsFixedPath(PathSuffix):
    def __init__(self, file_name: str):
        self._file_name = file_name

    @property
    def file_name(self) -> str:
        return self._file_name

    def resolve(self, symbols: SymbolTable) -> str:
        return self._file_name

    @property
    def value_references(self) -> list:
        return []


class PathSuffixAsStringSymbolReference(PathSuffix):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    def resolve(self, symbols: SymbolTable) -> str:
        raise NotImplementedError()

    @property
    def value_references(self) -> list:
        raise NotImplementedError()


class FileRef:
    """
    A reference to a file (any kind of file), with functionality to resolve it's path,
    and information about whether it exists pre SDS or not.
    """

    def __init__(self, file_name: str):
        self._path_suffix = PathSuffixAsFixedPath(file_name)
        self._file_name = file_name

    @property
    def path_suffix(self) -> PathSuffix:
        return self._path_suffix

    def path_suffix_str(self, symbols: SymbolTable) -> str:
        return self._path_suffix.resolve(symbols)

    def path_suffix_path(self, symbols: SymbolTable) -> pathlib.Path:
        return pathlib.Path(self.path_suffix_str(symbols))

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

    def relativity(self, value_definitions: SymbolTable) -> RelOptionType:
        # TODO [val-def] Return value should be able to denote absolute/no relativity
        raise NotImplementedError()

    def specific_relativity(self, value_definitions: SymbolTable) -> SpecificPathRelativity:
        # TODO [val-def] Rename to "relativity" when "relativity" can be replaced by this method.
        rel_option_type = self.relativity(value_definitions)
        return specific_relative_relativity(rel_option_type)

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


class PathSuffixVisitor:
    def visit(self, path_suffix: PathSuffix):
        if isinstance(path_suffix, PathSuffixAsFixedPath):
            return self.visit_fixed_path(path_suffix)
        elif isinstance(path_suffix, PathSuffixAsStringSymbolReference):
            return self.visit_symbol_reference(path_suffix)
        raise TypeError('Not a {}: {}'.format(str(PathSuffix), path_suffix))

    def visit_fixed_path(self, path_suffix: PathSuffixAsFixedPath):
        raise NotImplementedError()

    def visit_symbol_reference(self, path_suffix: PathSuffixAsStringSymbolReference):
        raise NotImplementedError()
