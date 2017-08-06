import pathlib

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure


def fake_hds() -> HomeDirectoryStructure:
    return HomeDirectoryStructure(case_dir=pathlib.Path('hds-case'),
                                  act_dir=pathlib.Path('hds-act'))


def fake_sds() -> SandboxDirectoryStructure:
    return SandboxDirectoryStructure('sds')


def fake_home_and_sds() -> HomeAndSds:
    return HomeAndSds(fake_hds(),
                      fake_sds())
