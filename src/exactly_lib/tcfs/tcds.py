from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.tcfs.sds import SandboxDs


class TestCaseDs:
    """Test Case Directory Structure"""

    def __init__(self,
                 hds: HomeDs,
                 sds: SandboxDs):
        self._hds = hds
        self._sds = sds

    @property
    def hds(self) -> HomeDs:
        return self._hds

    @property
    def sds(self) -> SandboxDs:
        return self._sds
