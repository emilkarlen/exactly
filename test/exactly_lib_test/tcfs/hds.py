import pathlib
import unittest

from exactly_lib.tcfs import hds as sut


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_construct_and_get_hds_case(self):
        # ARRANGE #
        case_dir = pathlib.Path('case')
        act_dir = pathlib.Path('act')
        # ACT #
        hds = sut.HomeDs(case_dir=case_dir, act_dir=act_dir)
        actual = hds.case_dir
        # ASSERT #
        self.assertEqual(case_dir,
                         actual)

    def test_construct_and_get_hds_act(self):
        # ARRANGE #
        case_dir = pathlib.Path('case')
        act_dir = pathlib.Path('act')
        # ACT #
        hds = sut.HomeDs(case_dir=case_dir, act_dir=act_dir)
        actual = hds.act_dir
        # ASSERT #
        self.assertEqual(act_dir,
                         actual)
