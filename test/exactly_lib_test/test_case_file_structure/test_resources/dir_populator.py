import pathlib

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.test_resources import file_structure


class HomeOrSdsPopulator:
    """
    Populates any directory, and may be a home directory or directory in SDS or current directory.
    """

    def populate_home_or_sds(self, home_or_sds: HomeAndSds):
        raise NotImplementedError()


class HomePopulator(HomeOrSdsPopulator):
    """
    Populates the home directory.
    """

    def __init__(self, home_dir_contents: file_structure.DirContents):
        self.home_dir_contents = home_dir_contents

    def populate_home(self, home_dir: pathlib.Path):
        self.home_dir_contents.write_to(home_dir)

    def populate_home_or_sds(self, home_or_sds: HomeAndSds):
        self.populate_home(home_or_sds.home_dir_path)


class NonHomePopulator(HomeOrSdsPopulator):
    """
    Populates a directory in SDS or current directory.
    """

    def populate_non_home(self, sds: SandboxDirectoryStructure):
        raise NotImplementedError()

    def populate_home_or_sds(self, home_or_sds: HomeAndSds):
        self.populate_non_home(home_or_sds.sds)


class SdsPopulator(NonHomePopulator):
    """
    Populates a directory inside the SDS
    """

    def populate_sds(self, sds: SandboxDirectoryStructure):
        raise NotImplementedError()

    def populate_non_home(self, sds: SandboxDirectoryStructure):
        self.populate_sds(sds)
