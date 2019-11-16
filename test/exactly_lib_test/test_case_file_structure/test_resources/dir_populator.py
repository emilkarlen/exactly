from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.test_case_file_structure.tcds import Tcds


class TcdsPopulator:
    """
    Populates any directory, and may be a home directory or directory in SDS or current directory.
    """

    def populate_tcds(self, tcds: Tcds):
        raise NotImplementedError()


class HdsPopulator(TcdsPopulator):
    """
    Populates the home directory structure.
    """

    def populate_hds(self, hds: HomeDirectoryStructure):
        raise NotImplementedError()

    def populate_tcds(self, tcds: Tcds):
        self.populate_hds(tcds.hds)


class NonHdsPopulator(TcdsPopulator):
    """
    Populates a directory in SDS or current directory.
    """

    def populate_non_hds(self, sds: SandboxDirectoryStructure):
        raise NotImplementedError()

    def populate_tcds(self, tcds: Tcds):
        self.populate_non_hds(tcds.sds)


class SdsPopulator(NonHdsPopulator):
    """
    Populates a directory inside the SDS
    """

    def populate_sds(self, sds: SandboxDirectoryStructure):
        raise NotImplementedError()

    def populate_non_hds(self, sds: SandboxDirectoryStructure):
        self.populate_sds(sds)
