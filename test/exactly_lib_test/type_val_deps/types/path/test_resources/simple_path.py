import pathlib
from typing import Optional

from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.tcfs.path_relativity import RelOptionType, DirectoryStructurePartition, \
    RESOLVING_DEPENDENCY_OF
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.type_val_deps.types.path import path_ddvs
from exactly_lib.type_val_deps.types.path.impl.path_base import PathDdvWithPathSuffixAndIsNotAbsoluteBase
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib.type_val_deps.types.path.path_part_ddv import PathPartDdv


def path_test_impl(file_name: str = 'path_test_impl',
                   relativity: RelOptionType = RelOptionType.REL_RESULT) -> PathDdv:
    return PathDdvTestImpl(relativity, path_ddvs.constant_path_part(file_name))


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

    def value_pre_sds(self, hds: HomeDs) -> pathlib.Path:
        return pathlib.Path(str(self.__relativity)) / self.path_suffix_path()

    def value_post_sds(self, sds: SandboxDs) -> pathlib.Path:
        return pathlib.Path(str(self.__relativity)) / self.path_suffix_path()

    def _relativity(self) -> RelOptionType:
        return self.__relativity
