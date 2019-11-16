from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure


class Tcds:
    """Test Case Directory Structure"""

    def __init__(self,
                 hds: HomeDirectoryStructure,
                 sds: SandboxDirectoryStructure):
        self._hds = hds
        self._sds = sds

    @property
    def hds(self) -> HomeDirectoryStructure:
        return self._hds

    @property
    def sds(self) -> SandboxDirectoryStructure:
        return self._sds
