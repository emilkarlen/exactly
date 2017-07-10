import pathlib

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure


def dummy_sds() -> SandboxDirectoryStructure:
    return SandboxDirectoryStructure('sds')


def dummy_home_and_sds() -> HomeAndSds:
    return HomeAndSds(pathlib.Path('home'),
                      dummy_sds())
