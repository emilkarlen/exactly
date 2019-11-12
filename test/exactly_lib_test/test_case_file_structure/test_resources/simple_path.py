import pathlib
from typing import Optional

from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, DirectoryStructurePartition, \
    RESOLVING_DEPENDENCY_OF
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.type_system.data import paths
from exactly_lib.type_system.data.impl.path.path_base import PathDdvWithPathSuffixAndIsNotAbsoluteBase
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib.type_system.data.path_part import PathPartDdv


def path_test_impl(file_name: str = 'path_test_impl',
                   relativity: RelOptionType = RelOptionType.REL_RESULT) -> PathDdv:
    return PathDdvTestImpl(relativity, paths.constant_path_part(file_name))


class PathDdvTestImpl(PathDdvWithPathSuffixAndIsNotAbsoluteBase):
    """
    A dummy PathDdv that has a given relativity,
    and is as simple as possible.
    """

    def __init__(self,
                 relativity: RelOptionType,
                 path_suffix: PathPartDdv):
        super().__init__(path_suffix)
        self.__relativity = relativity
        self.__path_suffix = path_suffix

    def resolving_dependency(self) -> Optional[DirectoryStructurePartition]:
        return RESOLVING_DEPENDENCY_OF[self.__relativity]

    def has_dir_dependency(self) -> bool:
        return True

    def value_pre_sds(self, hds: HomeDirectoryStructure) -> pathlib.Path:
        return pathlib.Path(str(self.__relativity)) / self.path_suffix_path()

    def value_post_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return pathlib.Path(str(self.__relativity)) / self.path_suffix_path()

    def _relativity(self) -> RelOptionType:
        return self.__relativity
