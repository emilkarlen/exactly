import pathlib
import unittest

from exactly_lib.test_case_file_structure import home_directory_structure as sut


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_construct_and_get_case_home(self):
        # ARRANGE #
        case_home = pathlib.Path('case_home')
        # ACT #
        actual = sut.HomeDirectoryStructure(case_home=case_home)
        # ASSERT #
        self.assertEqual(case_home,
                         actual.case_home)
