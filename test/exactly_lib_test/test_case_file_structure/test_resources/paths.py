import pathlib

from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.test_case_file_structure.tcds import Tcds


def fake_hds() -> HomeDirectoryStructure:
    """Gives a HDS with different sub-dirs for case, act."""
    return HomeDirectoryStructure(case_dir=pathlib.Path('hds-case'),
                                  act_dir=pathlib.Path('hds-act'))


def fake_sds() -> SandboxDirectoryStructure:
    return SandboxDirectoryStructure('sds')


def fake_tcds() -> Tcds:
    return Tcds(fake_hds(),
                fake_sds())
