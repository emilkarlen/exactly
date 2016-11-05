import pathlib
import unittest

from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class SideEffectsCheck:
    def apply(self,
              put: unittest.TestCase,
              home_and_sds: HomeAndSds):
        pass


class AssertCwdIsSubDirOfActDir(SideEffectsCheck):
    def __init__(self, expected_sub_dir_of_act_dir: pathlib.PurePath):
        self.expected_sub_dir_of_act_dir = expected_sub_dir_of_act_dir

    def apply(self,
              put: unittest.TestCase,
              home_and_sds: HomeAndSds):
        put.assertEqual(home_and_sds.sds.act_dir / self.expected_sub_dir_of_act_dir,
                        pathlib.Path.cwd())


class AdaptVa(SideEffectsCheck):
    def __init__(self,
                 va: ValueAssertion):
        self.va = va

    def apply(self,
              put: unittest.TestCase,
              home_and_sds: HomeAndSds):
        self.va.apply(put, home_and_sds)
