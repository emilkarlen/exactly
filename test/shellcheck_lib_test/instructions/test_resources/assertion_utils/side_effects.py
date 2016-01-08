import pathlib
import unittest

from shellcheck_lib.test_case.sections.common import HomeAndEds


class SideEffectsCheck:
    def apply(self,
              put: unittest.TestCase,
              home_and_eds: HomeAndEds):
        pass


class AssertCwdIsSubDirOfActDir(SideEffectsCheck):
    def __init__(self, expected_sub_dir_of_act_dir: pathlib.PurePath):
        self.expected_sub_dir_of_act_dir = expected_sub_dir_of_act_dir

    def apply(self,
              put: unittest.TestCase,
              home_and_eds: HomeAndEds):
        put.assertEqual(home_and_eds.eds.act_dir / self.expected_sub_dir_of_act_dir,
                        pathlib.Path.cwd())
