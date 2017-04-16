import pathlib

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_part import PathPart
from exactly_lib.test_case_file_structure.path_relativity import SpecificPathRelativity
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure


class FileRef:
    """
    A reference to a file (any kind of file), with functionality to resolve it's path,
    and information about whether it exists pre SDS or not.
    """

    def path_suffix(self) -> PathPart:
        raise NotImplementedError()

    def path_suffix_str(self) -> str:
        raise NotImplementedError()

    def path_suffix_path(self) -> pathlib.Path:
        raise NotImplementedError()

    def exists_pre_sds(self) -> bool:
        raise NotImplementedError()

    def relativity(self) -> SpecificPathRelativity:
        raise NotImplementedError()

    def file_path_pre_sds(self, home_dir_path: pathlib.Path) -> pathlib.Path:
        """
        :raises ValueError: This file exists only post-SDS.
        """
        raise NotImplementedError()

    def file_path_post_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        """
        :raises ValueError: This file exists pre-SDS.
        """
        raise NotImplementedError()

    def file_path_pre_or_post_sds(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        if self.exists_pre_sds():
            return self.file_path_pre_sds(home_and_sds.home_dir_path)
        else:
            return self.file_path_post_sds(home_and_sds.sds)
