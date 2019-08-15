from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer


class WithoutDependencies(Renderer[str]):
    def __init__(self, path_value: FileRef):
        self._path_value = path_value

    def render(self) -> str:
        return str(self._path_value.value_when_no_dir_dependencies())


class DependentOnHds(Renderer[str]):
    def __init__(self,
                 path_value: FileRef,
                 hds: HomeDirectoryStructure,
                 ):
        self._path_value = path_value
        self._hds = hds

    def render(self) -> str:
        return str(self._path_value.value_pre_sds(self._hds))


class DependentOnSds(Renderer[str]):
    def __init__(self,
                 path_value: FileRef,
                 sds: SandboxDirectoryStructure,
                 ):
        self._path_value = path_value
        self._sds = sds

    def render(self) -> str:
        return str(self._path_value.value_post_sds(self._sds))


class DependentOnAnything(Renderer[str]):
    def __init__(self,
                 path_value: FileRef,
                 tcds: HomeAndSds,
                 ):
        self._path_value = path_value
        self._tcds = tcds

    def render(self) -> str:
        return str(self._path_value.value_of_any_dependency(self._tcds))
