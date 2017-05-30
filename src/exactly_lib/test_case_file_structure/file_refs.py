import pathlib

from exactly_lib.test_case_file_structure import relativity_root, relative_path_options
from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.test_case_file_structure.file_ref_base import FileRefWithPathSuffixBase, \
    FileRefWithPathSuffixAndIsNotAbsoluteBase
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_part import PathPart
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, SpecificPathRelativity, \
    SPECIFIC_ABSOLUTE_RELATIVITY
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure


class _FileRefWithConstantLocationBase(FileRefWithPathSuffixAndIsNotAbsoluteBase):
    """
    Base class for `FileRef`s who's "relativity" is constant.
    """

    def __init__(self, exists_pre_sds: bool, path_suffix: PathPart):
        super().__init__(path_suffix)
        self.__exists_pre_sds = exists_pre_sds

    def exists_pre_sds(self) -> bool:
        return self.__exists_pre_sds

    def file_path_pre_or_post_sds(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        if self.__exists_pre_sds:
            return self.file_path_pre_sds(home_and_sds.home_dir_path)
        else:
            return self.file_path_post_sds(home_and_sds.sds)


class _FileRefFromRelRootResolver(_FileRefWithConstantLocationBase):
    def __init__(self,
                 rel_root_resolver: relativity_root.RelRootResolver,
                 path_suffix: PathPart):
        super().__init__(rel_root_resolver.is_rel_home, path_suffix)
        self._rel_root_resolver = rel_root_resolver

    def _relativity(self) -> RelOptionType:
        return self._rel_root_resolver.relativity_type

    def file_path_pre_sds(self, home_dir_path: pathlib.Path) -> pathlib.Path:
        suffix = self.path_suffix_path()
        root = self._rel_root_resolver.from_home(home_dir_path)
        return root / suffix

    def file_path_post_sds(self, sds: SandboxDirectoryStructure):
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
    return of_rel_root(relativity_root.resolver_for_home, path_suffix)


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

    def exists_pre_sds(self) -> bool:
        return True

    def file_path_pre_or_post_sds(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        return self.file_path_pre_sds(home_and_sds.home_dir_path)

    def file_path_pre_sds(self, home_dir_path: pathlib.Path) -> pathlib.Path:
        return self.path_suffix_path()

    def file_path_post_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        raise ValueError('This file exists pre-SDS')


class _FileRefRelHome(_FileRefWithConstantLocationBase):
    def __init__(self, path_suffix: PathPart):
        super().__init__(True, path_suffix)

    def file_path_pre_sds(self, home_dir_path: pathlib.Path) -> pathlib.Path:
        return home_dir_path / self.path_suffix_path()

    def file_path_post_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        raise ValueError('This file exists pre-SDS')


class _FileRefRelTmpInternal(_FileRefWithConstantLocationBase):
    def __init__(self, path_suffix: PathPart):
        super().__init__(False, path_suffix)

    def file_path_pre_sds(self, home_dir_path: pathlib.Path) -> pathlib.Path:
        raise ValueError('This file does not exist pre-SDS')

    def file_path_post_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return sds.tmp.internal_dir / self.path_suffix_path()
