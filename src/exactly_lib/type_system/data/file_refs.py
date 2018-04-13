import pathlib

from exactly_lib.test_case_file_structure import relativity_root, relative_path_options
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependencyError
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, SpecificPathRelativity, \
    SPECIFIC_ABSOLUTE_RELATIVITY, DirectoryStructurePartition, rel_any_from_rel_home
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.type_system.data import concrete_path_parts
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.data.file_ref_base import FileRefWithPathSuffixBase, \
    FileRefWithPathSuffixAndIsNotAbsoluteBase
from exactly_lib.type_system.data.path_part import PathPart


def constant_path_part(file_name: str) -> PathPart:
    return concrete_path_parts.PathPartAsFixedPath(file_name)


def empty_path_part() -> PathPart:
    return concrete_path_parts.PathPartAsNothing()


def of_rel_root(rel_root_resolver: relativity_root.RelRootResolver,
                path_suffix: PathPart = empty_path_part()) -> FileRef:
    return _FileRefFromRelRootResolver(rel_root_resolver, path_suffix)


def of_rel_option(rel_option: relativity_root.RelOptionType,
                  path_suffix: PathPart = empty_path_part()) -> FileRef:
    return _FileRefFromRelRootResolver(relative_path_options.REL_OPTIONS_MAP[rel_option].root_resolver,
                                       path_suffix)


def simple_of_rel_option(rel_option: relativity_root.RelOptionType,
                         file_name: str) -> FileRef:
    return of_rel_option(rel_option, constant_path_part(file_name))


def absolute_file_name(file_name: str) -> FileRef:
    return _FileRefAbsolute(constant_path_part(file_name))


def absolute_path(abs_path: pathlib.Path) -> FileRef:
    return absolute_file_name(str(abs_path))


def rel_home(rel_option: relativity_root.RelHomeOptionType,
             path_suffix: PathPart) -> FileRef:
    return _FileRefRelHome(rel_option, path_suffix)


def rel_home_case(path_suffix: PathPart) -> FileRef:
    return rel_home(relativity_root.RelHomeOptionType.REL_HOME_CASE, path_suffix)


def rel_home_act(path_suffix: PathPart) -> FileRef:
    return rel_home(relativity_root.RelHomeOptionType.REL_HOME_ACT, path_suffix)


def rel_cwd(path_suffix: PathPart) -> FileRef:
    return of_rel_root(relativity_root.resolver_for_cwd, path_suffix)


def rel_sandbox(rel_option: relativity_root.RelSdsOptionType,
                path_suffix: PathPart) -> FileRef:
    return of_rel_root(relative_path_options.REL_SDS_OPTIONS_MAP[rel_option].root_resolver,
                       path_suffix)


def rel_act(path_suffix: PathPart) -> FileRef:
    return of_rel_root(relativity_root.resolver_for_act, path_suffix)


def rel_tmp_user(path_suffix: PathPart) -> FileRef:
    return of_rel_root(relativity_root.resolver_for_tmp_user, path_suffix)


def rel_result(path_suffix: PathPart) -> FileRef:
    return of_rel_root(relativity_root.resolver_for_result, path_suffix)


class _FileRefWithConstantLocationBase(FileRefWithPathSuffixAndIsNotAbsoluteBase):
    """
    Base class for `FileRef`s who's "relativity" is constant.
    """

    def __init__(self, path_suffix: PathPart):
        super().__init__(path_suffix)


class _FileRefFromRelRootResolver(_FileRefWithConstantLocationBase):
    def __init__(self,
                 rel_root_resolver: relativity_root.RelRootResolver,
                 path_suffix: PathPart):
        super().__init__(path_suffix)
        self._rel_root_resolver = rel_root_resolver

    def _relativity(self) -> RelOptionType:
        return self._rel_root_resolver.relativity_type

    def has_dir_dependency(self) -> bool:
        return True

    def value_pre_sds(self, hds: HomeDirectoryStructure) -> pathlib.Path:
        suffix = self.path_suffix_path()
        root = self._rel_root_resolver.from_home(hds)
        return root / suffix

    def value_post_sds(self, sds: SandboxDirectoryStructure):
        suffix = self.path_suffix_path()
        root = self._rel_root_resolver.from_non_home(sds)
        return root / suffix


class _FileRefAbsolute(FileRefWithPathSuffixBase):
    def __init__(self, path_suffix: PathPart):
        super().__init__(path_suffix)

    def relativity(self) -> SpecificPathRelativity:
        return SPECIFIC_ABSOLUTE_RELATIVITY

    def has_dir_dependency(self) -> bool:
        return False

    def value_when_no_dir_dependencies(self) -> pathlib.Path:
        return self.path_suffix_path()

    def value_pre_sds(self, hds: HomeDirectoryStructure) -> pathlib.Path:
        return self.value_when_no_dir_dependencies()

    def value_post_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self.value_when_no_dir_dependencies()


class _FileRefRelHome(_FileRefWithConstantLocationBase):
    def __init__(self,
                 rel_option: relativity_root.RelHomeOptionType,
                 path_suffix: PathPart):
        super().__init__(path_suffix)
        self._rel_option = rel_option

    def has_dir_dependency(self) -> bool:
        return True

    def value_when_no_dir_dependencies(self) -> pathlib.Path:
        raise DirDependencyError({DirectoryStructurePartition.HOME})

    def value_pre_sds(self, hds: HomeDirectoryStructure) -> pathlib.Path:
        suffix = self.path_suffix_path()
        root = relative_path_options.REL_HOME_OPTIONS_MAP[self._rel_option].root_resolver.from_home(hds)
        return root / suffix

    def value_post_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        raise DirDependencyError({DirectoryStructurePartition.HOME},
                                 'This file exists pre-SDS')

    def _relativity(self) -> RelOptionType:
        return rel_any_from_rel_home(self._rel_option)
