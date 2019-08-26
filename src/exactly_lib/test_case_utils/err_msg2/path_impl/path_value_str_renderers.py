import pathlib

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.err_msg import path_description
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer


class PathValueRelTcdsDir(Renderer[str]):
    def __init__(self, path_value: FileRef):
        self._path_value = path_value

    def render(self) -> str:
        return path_description.path_value_with_relativity_name_prefix__rel_tcds_dir(self._path_value)


class PathValueRelCwd(Renderer[str]):
    def __init__(self,
                 path_value: FileRef,
                 cwd: pathlib.Path,
                 tcds: HomeAndSds,
                 ):
        self._path_value = path_value
        self._cwd = cwd
        self._tcds = tcds

    def render(self) -> str:
        return path_description.path_value_with_relativity_name_prefix(
            self._path_value,
            self._tcds,
            self._cwd,
        )


class PathValueRelJustCwd(Renderer[str]):
    def __init__(self,
                 path_value: FileRef,
                 cwd: pathlib.Path,
                 ):
        self._path_value = path_value
        self._cwd = cwd

    def render(self) -> str:
        return str(self._cwd / self._path_value.path_suffix_path())


class PathValueRelUnknownCwd(Renderer[str]):
    def __init__(self,
                 path_value: FileRef,
                 ):
        self._path_value = path_value

    def render(self) -> str:
        return str(_CURRENT_DIRECTORY / self._path_value.path_suffix_path())


class PathValueAbsolute(Renderer[str]):
    def __init__(self,
                 path_value: FileRef,
                 tcds: HomeAndSds,
                 ):
        self._path_value = path_value
        self._tcds = tcds

    def render(self) -> str:
        return path_description.path_value_with_relativity_name_prefix(
            self._path_value,
            self._tcds,
            None,
        )


class PathValuePlainAbsolute(Renderer[str]):
    def __init__(self,
                 path_value: FileRef,
                 ):
        self._path_value = path_value

    def render(self) -> str:
        return str(self._path_value.value_when_no_dir_dependencies())


class _PathStrRendererForNotImplemented(Renderer[str]):
    def render(self) -> str:
        raise NotImplementedError('must not be used')


_CURRENT_DIRECTORY = pathlib.Path('<CURRENT-DIRECTORY>')
