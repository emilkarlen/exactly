from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.tcfs.tcds import TestCaseDs


class TcdsPopulator:
    """
    Populates any directory, and may be a home directory or directory in SDS or current directory.
    """

    @staticmethod
    def empty() -> 'TcdsPopulator':
        return _SdsPopulatorEmpty()

    def populate_tcds(self, tcds: TestCaseDs):
        raise NotImplementedError()


class HdsPopulator(TcdsPopulator):
    """
    Populates the home directory structure.
    """

    @staticmethod
    def empty() -> '_HdsPopulatorEmpty':
        return _HdsPopulatorEmpty()

    def populate_hds(self, hds: HomeDs):
        raise NotImplementedError()

    def populate_tcds(self, tcds: TestCaseDs):
        self.populate_hds(tcds.hds)


class NonHdsPopulator(TcdsPopulator):
    """
    Populates a directory in SDS or current directory.
    """

    @staticmethod
    def empty() -> 'NonHdsPopulator':
        return _SdsPopulatorEmpty()

    def populate_non_hds(self, sds: SandboxDs):
        raise NotImplementedError()

    def populate_tcds(self, tcds: TestCaseDs):
        self.populate_non_hds(tcds.sds)


class SdsPopulator(NonHdsPopulator):
    """
    Populates a directory inside the SDS
    """

    @staticmethod
    def empty() -> 'SdsPopulator':
        return _SdsPopulatorEmpty()

    def populate_sds(self, sds: SandboxDs):
        raise NotImplementedError()

    def populate_non_hds(self, sds: SandboxDs):
        self.populate_sds(sds)


class _SdsPopulatorEmpty(SdsPopulator):
    def populate_sds(self, sds: SandboxDs):
        pass


class _HdsPopulatorEmpty(HdsPopulator):
    def populate_hds(self, hds: HomeDs):
        pass
