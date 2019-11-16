import pathlib
from abc import ABC

from exactly_lib.test_case_file_structure import relativity_root, relative_path_options
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependencyError
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, SpecificPathRelativity, \
    SPECIFIC_ABSOLUTE_RELATIVITY, DirectoryStructurePartition, rel_any_from_rel_hds
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.type_system.data import concrete_path_parts
from exactly_lib.type_system.data.concrete_path_parts import PathPartDdvAsNothing
from exactly_lib.type_system.data.impl.path.path_base import PathDdvWithPathSuffixBase, \
    PathDdvWithPathSuffixAndIsNotAbsoluteBase, PathDdvWithDescriptionBase
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib.type_system.data.path_part import PathPartDdv


def constant_path_part(file_name: str) -> PathPartDdv:
    return concrete_path_parts.PathPartDdvAsFixedPath(file_name)


def empty_path_part() -> PathPartDdv:
    return concrete_path_parts.PathPartDdvAsNothing()


def of_rel_root(rel_root_resolver: relativity_root.RelRootResolver,
                path_suffix: PathPartDdv = empty_path_part()) -> PathDdv:
    return _PathDdvFromRelRootResolver(rel_root_resolver, path_suffix)


def of_rel_option(rel_option: relativity_root.RelOptionType,
                  path_suffix: PathPartDdv = empty_path_part()) -> PathDdv:
    return _PathDdvFromRelRootResolver(relative_path_options.REL_OPTIONS_MAP[rel_option].root_resolver,
                                       path_suffix)


def simple_of_rel_option(rel_option: relativity_root.RelOptionType,
                         file_name: str) -> PathDdv:
    return of_rel_option(rel_option, constant_path_part(file_name))


def absolute_file_name(file_name: str) -> PathDdv:
    return _PathDdvAbsolute(constant_path_part(file_name))


def absolute_path(abs_path: pathlib.Path) -> PathDdv:
    return absolute_file_name(str(abs_path))


def absolute_part(abs_path: PathPartDdv) -> PathDdv:
    return _PathDdvAbsolute(abs_path)


def rel_abs_path(abs_path_root: pathlib.Path,
                 path_suffix: PathPartDdv) -> PathDdv:
    return absolute_file_name(str(abs_path_root / path_suffix.value()))


def rel_hds(rel_option: relativity_root.RelHdsOptionType,
            path_suffix: PathPartDdv) -> PathDdv:
    return _PathDdvRelHds(rel_option, path_suffix)


def rel_hds_case(path_suffix: PathPartDdv) -> PathDdv:
    return rel_hds(relativity_root.RelHdsOptionType.REL_HDS_CASE, path_suffix)


def rel_hds_act(path_suffix: PathPartDdv) -> PathDdv:
    return rel_hds(relativity_root.RelHdsOptionType.REL_HDS_ACT, path_suffix)


def rel_cwd(path_suffix: PathPartDdv) -> PathDdv:
    return of_rel_root(relativity_root.resolver_for_cwd, path_suffix)


def rel_sandbox(rel_option: relativity_root.RelSdsOptionType,
                path_suffix: PathPartDdv) -> PathDdv:
    return of_rel_root(relative_path_options.REL_SDS_OPTIONS_MAP[rel_option].root_resolver,
                       path_suffix)


def rel_act(path_suffix: PathPartDdv) -> PathDdv:
    return of_rel_root(relativity_root.resolver_for_act, path_suffix)


def rel_tmp_user(path_suffix: PathPartDdv) -> PathDdv:
    return of_rel_root(relativity_root.resolver_for_tmp_user, path_suffix)


def rel_result(path_suffix: PathPartDdv) -> PathDdv:
    return of_rel_root(relativity_root.resolver_for_result, path_suffix)


def stacked(base_path: PathDdv, path_suffix: PathPartDdv) -> PathDdv:
    return _StackedPathDdv(base_path, path_suffix)


class _PathDdvWithConstantLocationBase(PathDdvWithPathSuffixAndIsNotAbsoluteBase, ABC):
    """
    Base class for `PathDdv`s who's "relativity" is constant.
    """

    def __init__(self, path_suffix: PathPartDdv):
        super().__init__(path_suffix)


class _PathDdvFromRelRootResolver(_PathDdvWithConstantLocationBase):
    def __init__(self,
                 rel_root_resolver: relativity_root.RelRootResolver,
                 path_suffix: PathPartDdv):
        super().__init__(path_suffix)
        self._rel_root_resolver = rel_root_resolver

    def _relativity(self) -> RelOptionType:
        return self._rel_root_resolver.relativity_type

    def has_dir_dependency(self) -> bool:
        return True

    def value_pre_sds(self, hds: HomeDirectoryStructure) -> pathlib.Path:
        suffix = self.path_suffix_path()
        root = self._rel_root_resolver.from_hds(hds)
        return root / suffix

    def value_post_sds(self, sds: SandboxDirectoryStructure):
        suffix = self.path_suffix_path()
        root = self._rel_root_resolver.from_non_hds(sds)
        return root / suffix


class _PathDdvAbsolute(PathDdvWithPathSuffixBase):
    def __init__(self, path_suffix: PathPartDdv):
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


class _PathDdvRelHds(_PathDdvWithConstantLocationBase):
    def __init__(self,
                 rel_option: relativity_root.RelHdsOptionType,
                 path_suffix: PathPartDdv):
        super().__init__(path_suffix)
        self._rel_option = rel_option

    def has_dir_dependency(self) -> bool:
        return True

    def value_when_no_dir_dependencies(self) -> pathlib.Path:
        raise DirDependencyError({DirectoryStructurePartition.HDS})

    def value_pre_sds(self, hds: HomeDirectoryStructure) -> pathlib.Path:
        suffix = self.path_suffix_path()
        root = relative_path_options.REL_HDS_OPTIONS_MAP[self._rel_option].root_resolver.from_hds(hds)
        return root / suffix

    def value_post_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        raise DirDependencyError({DirectoryStructurePartition.HDS},
                                 'This file exists pre-SDS')

    def _relativity(self) -> RelOptionType:
        return rel_any_from_rel_hds(self._rel_option)


class _StackedPathDdv(PathDdvWithDescriptionBase):
    def __init__(self, base_path: PathDdv, path_suffix: PathPartDdv):
        self._stacked_path_suffix = path_suffix
        self._combined_path_suffix = self._combine(base_path.path_suffix(), path_suffix)
        self.base_path = base_path

    def relativity(self) -> SpecificPathRelativity:
        return self.base_path.relativity()

    def path_suffix(self) -> PathPartDdv:
        return self._combined_path_suffix

    def path_suffix_str(self) -> str:
        return self._combined_path_suffix.value()

    def path_suffix_path(self) -> pathlib.Path:
        return pathlib.Path(self.path_suffix_str())

    def _stacked_path_suffix_path(self) -> pathlib.Path:
        return pathlib.Path(self._stacked_path_suffix.value())

    def has_dir_dependency(self) -> bool:
        return self.base_path.has_dir_dependency()

    def value_when_no_dir_dependencies(self) -> pathlib.Path:
        return self.base_path.value_when_no_dir_dependencies() / self._stacked_path_suffix_path()

    def value_pre_sds(self, hds: HomeDirectoryStructure) -> pathlib.Path:
        return self.base_path.value_pre_sds(hds) / self._stacked_path_suffix_path()

    def value_post_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self.base_path.value_post_sds(sds) / self._stacked_path_suffix_path()

    @staticmethod
    def _combine(first: PathPartDdv, second: PathPartDdv) -> PathPartDdv:
        if isinstance(first, PathPartDdvAsNothing):
            return second
        if isinstance(second, PathPartDdvAsNothing):
            return first
        p = pathlib.Path(first.value()) / pathlib.Path(second.value())
        return constant_path_part(str(p))
