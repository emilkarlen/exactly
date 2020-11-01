import pathlib

from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.tcfs.tcds import TestCaseDs


def fake_hds() -> HomeDs:
    """Gives a HDS with different sub-dirs for case, act."""
    return HomeDs(case_dir=pathlib.Path('/exactly-test-dummy-fs/hds-case'),
                  act_dir=pathlib.Path('/exactly-test-dummy-fs/hds-act'))


def fake_sds() -> SandboxDs:
    return SandboxDs('/exactly-test-dummy-fs/sds')


def fake_tcds() -> TestCaseDs:
    return TestCaseDs(fake_hds(), fake_sds())
