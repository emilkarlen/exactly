import pathlib

from exactly_lib.test_case.home_and_sds import HomeAndSds
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure


class PathResolvingEnvironment:
    """
    Base class for information needed for resolving paths, outside or inside the SDS.
    """
    pass


class PathResolvingEnvironmentPreSds(PathResolvingEnvironment):
    def __init__(self, home_dir_path: pathlib.Path):
        self._home_dir_path = home_dir_path

    @property
    def home_dir_path(self):
        return self._home_dir_path


class PathResolvingEnvironmentPostSds(PathResolvingEnvironment):
    def __init__(self, sds: SandboxDirectoryStructure):
        self._sds = sds

    @property
    def sds(self) -> SandboxDirectoryStructure:
        return self._sds


class PathResolvingEnvironmentPreOrPostSds(PathResolvingEnvironmentPreSds, PathResolvingEnvironmentPostSds):
    def __init__(self, home_and_sds: HomeAndSds):
        PathResolvingEnvironmentPreSds.__init__(self, home_and_sds.home_dir_path)
        PathResolvingEnvironmentPostSds.__init__(self, home_and_sds.sds)
        self._home_and_sds = home_and_sds

    @property
    def home_and_sds(self) -> HomeAndSds:
        return self._home_and_sds
