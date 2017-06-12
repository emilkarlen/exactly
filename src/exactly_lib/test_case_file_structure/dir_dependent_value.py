import pathlib
from enum import Enum

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import ResolvingDependency
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure


class DirDependency(Enum):
    NONE = 0
    HOME = 1
    SDS = 2
    HOME_AND_SDS = 3


class DirDependencyError(ValueError):
    def __init__(self, unexpected_dependency: ResolvingDependency,
                 msg: str = ''):
        super().__init__(msg)
        self.unexpected_dependency = unexpected_dependency

    def __str__(self) -> str:
        return '{}(unexpected={}: {})'.format(type(self),
                                              self.unexpected_dependency,
                                              super().__str__())


class DirDependentValue:
    """
    A value that may refer to the test case directories.
    """

    def has_dir_dependency(self) -> bool:
        """
        Tells whether or not the evaluation of this object uses any of the test case directories.
        :return:
        """
        raise NotImplementedError()

    def exists_pre_sds(self) -> bool:
        raise NotImplementedError()

    def value_when_no_dir_dependencies(self):
        """
        :raises DirDependencyError: This value has dir dependencies.
        """
        raise NotImplementedError()

    def value_pre_sds(self, home_dir_path: pathlib.Path):
        """
        :raises DirDependencyError: This file exists only post-SDS.
        """
        raise NotImplementedError()

    def value_post_sds(self, sds: SandboxDirectoryStructure):
        """
        :raises DirDependencyError: This file exists pre-SDS.
        """
        raise NotImplementedError()

    def value_pre_or_post_sds(self, home_and_sds: HomeAndSds):
        if self.exists_pre_sds():
            return self.value_pre_sds(home_and_sds.home_dir_path)
        else:
            return self.value_post_sds(home_and_sds.sds)
