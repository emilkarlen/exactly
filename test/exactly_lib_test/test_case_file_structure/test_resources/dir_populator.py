from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure


class HomeOrSdsPopulator:
    """
    Populates any directory, and may be a home directory or directory in SDS or current directory.
    """

    def populate_home_or_sds(self, home_or_sds: HomeAndSds):
        raise NotImplementedError()


class HomePopulator(HomeOrSdsPopulator):
    """
    Populates the home directory structure.
    """

    def populate_hds(self, hds: HomeDirectoryStructure):
        raise NotImplementedError()

    def populate_home_or_sds(self, home_or_sds: HomeAndSds):
        self.populate_hds(home_or_sds.hds)


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
