import pathlib

from exactly_lib.test_case_file_structure import relativity_root, relative_path_options
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependencyError
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, SpecificPathRelativity, \
    SPECIFIC_ABSOLUTE_RELATIVITY, ResolvingDependency
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.type_system_values.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.type_system_values.file_ref import FileRef
from exactly_lib.type_system_values.file_ref_base import FileRefWithPathSuffixBase, \
    FileRefWithPathSuffixAndIsNotAbsoluteBase
from exactly_lib.type_system_values.path_part import PathPart


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
        root = self._rel_root_resolver.from_home_hds(hds)
        return root / suffix

    def value_post_sds(self, sds: SandboxDirectoryStructure):
        suffix = self.path_suffix_path()
        root = self._rel_root_resolver.from_non_home(sds)
        return root / suffix


def of_rel_root(rel_root_resolver: relativity_root.RelRootResolver,
                path_suffix: PathPart) -> FileRef:
    return _FileRefFromRelRootResolver(rel_root_resolver, path_suffix)


def of_rel_option(rel_option: relativity_root.RelOptionType,
                  path_suffix: PathPart) -> FileRef:
    return _FileRefFromRelRootResolver(relative_path_options.REL_OPTIONS_MAP[rel_option].root_resolver,
                                       path_suffix)


def absolute_file_name(file_name: str) -> FileRef:
    return _FileRefAbsolute(PathPartAsFixedPath(file_name))


def rel_home(path_suffix: PathPart) -> FileRef:
    return of_rel_root(relativity_root.resolver_for_home_case, path_suffix)


def rel_cwd(path_suffix: PathPart) -> FileRef:
    return of_rel_root(relativity_root.resolver_for_cwd, path_suffix)


def rel_act(path_suffix: PathPart) -> FileRef:
    return of_rel_root(relativity_root.resolver_for_act, path_suffix)


def rel_tmp_user(path_suffix: PathPart) -> FileRef:
    return of_rel_root(relativity_root.resolver_for_tmp_user, path_suffix)


def rel_result(path_suffix: PathPart) -> FileRef:
    return of_rel_root(relativity_root.resolver_for_result, path_suffix)


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
    def __init__(self, path_suffix: PathPart):
        super().__init__(path_suffix)

    def has_dir_dependency(self) -> bool:
        return True

    def value_when_no_dir_dependencies(self) -> pathlib.Path:
        raise DirDependencyError(ResolvingDependency.HOME)

    def value_pre_sds(self, hds: HomeDirectoryStructure) -> pathlib.Path:
        return hds.case_dir / self.path_suffix_path()

    def value_post_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        raise DirDependencyError(ResolvingDependency.HOME,
                                 'This file exists pre-SDS')


class _FileRefRelTmpInternal(_FileRefWithConstantLocationBase):
    def __init__(self, path_suffix: PathPart):
        super().__init__(path_suffix)

    def has_dir_dependency(self) -> bool:
        return True

    def value_pre_sds(self, hds: HomeDirectoryStructure) -> pathlib.Path:
        raise DirDependencyError(ResolvingDependency.NON_HOME,
                                 'This file does not exist pre-SDS')

    def value_post_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return sds.tmp.internal_dir / self.path_suffix_path()
