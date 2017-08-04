import pathlib

from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure


class HomeAndSds:
    def __init__(self,
                 home_path: pathlib.Path,
                 sds: SandboxDirectoryStructure):
        self._hds = HomeDirectoryStructure(case_home=home_path)
        self._sds = sds

    @property
    def home_dir_path(self) -> pathlib.Path:
        return self._hds.case_dir

    @property
    def hds(self) -> HomeDirectoryStructure:
        return self._hds

    @property
    def sds(self) -> SandboxDirectoryStructure:
        return self._sds
