import pathlib

from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.test_case_file_structure.file_ref_base import FileRefWithPathSuffixAndIsNotAbsoluteBase
from exactly_lib.test_case_file_structure.path_part import PathPart
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure


def file_ref_test_impl(file_name: str = 'file_ref_test_impl',
                       relativity: RelOptionType = RelOptionType.REL_RESULT) -> FileRef:
    return FileRefTestImpl(relativity, PathPartAsFixedPath(file_name))


class FileRefTestImpl(FileRefWithPathSuffixAndIsNotAbsoluteBase):
    """
    A dummy FileRef that has a given relativity,
    and is as simple as possible.
    """

    def __init__(self,
                 relativity: RelOptionType,
                 path_suffix: PathPart):
        super().__init__(path_suffix)
        self.__relativity = relativity
        self.__path_suffix = path_suffix

    def exists_pre_sds(self) -> bool:
        return self.__relativity == RelOptionType.REL_HOME

    def file_path_pre_sds(self, home_dir_path: pathlib.Path) -> pathlib.Path:
        return pathlib.Path(str(self.__relativity)) / self.path_suffix_path()

    def file_path_post_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return pathlib.Path(str(self.__relativity)) / self.path_suffix_path()

    def _relativity(self) -> RelOptionType:
        return self.__relativity
