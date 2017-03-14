import pathlib

from exactly_lib.test_case_file_structure import sandbox_directory_structure as _sds


class HomeAndSds:
    def __init__(self,
                 home_path: pathlib.Path,
                 sds: _sds.SandboxDirectoryStructure):
        self._home_path = home_path
        self._sds = sds

    @property
    def home_dir_path(self) -> pathlib.Path:
        return self._home_path

    @property
    def sds(self) -> _sds.SandboxDirectoryStructure:
        return self._sds
