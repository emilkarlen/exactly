import pathlib
import unittest

from exactly_lib.test_case_file_structure import home_and_sds as sut
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib_test.test_case_file_structure.test_resources.paths import dummy_sds


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_construct_and_get_hds(self):
        # ARRANGE #
        case_home = pathlib.Path('case_home')
        sds = dummy_sds()
        # ACT #
        home_and_sds = sut.HomeAndSds(case_home, sds)
        actual_hds = home_and_sds.hds
        actual_home_dir_path = actual_hds.case_dir
        # ASSERT #
        self.assertIsInstance(actual_hds,
                              HomeDirectoryStructure)
        self.assertEqual(case_home,
                         actual_home_dir_path,
                         'short cut to case home')

    def test_construct_and_get_home_case_dir_via_short_cut(self):
        # ARRANGE #
        case_home = pathlib.Path('case_home')
        sds = dummy_sds()
        # ACT #
        home_and_sds = sut.HomeAndSds(case_home, sds)
        actual = home_and_sds.home_dir_path
        # ASSERT #
        self.assertEqual(case_home,
                         actual,
                         'short cut to case home')

    def test_construct_and_get_sds(self):
        # ARRANGE #
        case_home = pathlib.Path('case_home')
        sds = dummy_sds()
        # ACT #
        home_and_sds = sut.HomeAndSds(case_home, sds)
        actual = home_and_sds.sds
        # ASSERT #
        self.assertIs(actual, sds)
