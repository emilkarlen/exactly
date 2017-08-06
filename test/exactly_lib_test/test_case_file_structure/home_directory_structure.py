import pathlib
import unittest

from exactly_lib.test_case_file_structure import home_directory_structure as sut


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_construct_and_get_case_home(self):
        # ARRANGE #
        case_dir = pathlib.Path('case')
        act_dir = pathlib.Path('act')
        # ACT #
        hds = sut.HomeDirectoryStructure(case_dir=case_dir, act_dir=act_dir)
        actual = hds.case_dir
        # ASSERT #
        self.assertEqual(case_dir,
                         actual)

    def test_construct_and_get_home_act(self):
        # ARRANGE #
        case_dir = pathlib.Path('case')
        act_dir = pathlib.Path('act')
        # ACT #
        hds = sut.HomeDirectoryStructure(case_dir=case_dir, act_dir=act_dir)
        actual = hds.act_dir
        # ASSERT #
        self.assertEqual(act_dir,
                         actual)
