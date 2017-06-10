import pathlib

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure


class DirDependencyError(ValueError):
    def __init__(self, *args):
        super().__init__(*args)


class DirDependentValue:
    """
    A value that may refer to the test case directories.
    """

    def exists_pre_sds(self) -> bool:
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
