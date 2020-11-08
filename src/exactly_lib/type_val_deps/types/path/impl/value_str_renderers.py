import pathlib

from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.util.render.renderer import Renderer
from . import path_description
from ..path_ddv import PathDdv


class PathValueRelTcdsDir(Renderer[str]):
    def __init__(self, path_ddv: PathDdv):
        self._path_ddv = path_ddv

    def render(self) -> str:
        return path_description.path_ddv_with_relativity_name_prefix__rel_tcds_dir(self._path_ddv)


class PathValueRelCwd(Renderer[str]):
    def __init__(self,
                 path_ddv: PathDdv,
                 cwd: pathlib.Path,
                 tcds: TestCaseDs,
                 ):
        self._path_ddv = path_ddv
        self._cwd = cwd
        self._tcds = tcds

    def render(self) -> str:
        return path_description.path_ddv_with_relativity_name_prefix(
            self._path_ddv,
            self._tcds,
            self._cwd,
        )


class PathValueRelUnknownCwd(Renderer[str]):
    def __init__(self,
                 path_ddv: PathDdv,
                 ):
        self._path_ddv = path_ddv

    def render(self) -> str:
        return str(_CURRENT_DIRECTORY / self._path_ddv.path_suffix_path())


class PathValueAbsolute(Renderer[str]):
    def __init__(self,
                 path_ddv: PathDdv,
                 tcds: TestCaseDs,
                 ):
        self._path_ddv = path_ddv
        self._tcds = tcds

    def render(self) -> str:
        return path_description.path_ddv_with_relativity_name_prefix(
            self._path_ddv,
            self._tcds,
            None,
        )


class PathValuePlainAbsolute(Renderer[str]):
    def __init__(self,
                 path_ddv: PathDdv,
                 ):
        self._path_ddv = path_ddv

    def render(self) -> str:
        return str(self._path_ddv.value_when_no_dir_dependencies())


_CURRENT_DIRECTORY = pathlib.Path('<CURRENT-DIRECTORY>')
