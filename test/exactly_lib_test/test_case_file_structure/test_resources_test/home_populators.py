import unittest

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib_test.test_case_file_structure.test_resources import home_populators as sut
from exactly_lib_test.test_case_file_structure.test_resources.hds_utils import home_directory_structure
from exactly_lib_test.test_case_file_structure.test_resources.paths import dummy_sds
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources.value_assertions import file_assertions as f_asrt


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestCaseHomeDirPopulator)


class TestCaseHomeDirPopulator(unittest.TestCase):
    def test_populate_home__TO_BE_REMOVED(self):
        # TODO remove this test when populate_home is removed

        # ARRANGE #
        expected_dir_contents = fs.DirContents([fs.File('file-name.txt', 'file contents')])
        populator = sut.case_home_dir_contents(expected_dir_contents)
        expectation = f_asrt.dir_contains_exactly(expected_dir_contents)

        with home_directory_structure() as hds:
            # ACT #
            populator.populate_home(hds.case_dir)
            # ASSERT #
            expectation.apply_with_message(self, hds.case_dir,
                                           'contents of home/case dir')

    def test_populate_hds(self):
        # ARRANGE #
        expected_dir_contents = fs.DirContents([fs.File('file-name.txt', 'file contents')])
        populator = sut.case_home_dir_contents(expected_dir_contents)
        expectation = f_asrt.dir_contains_exactly(expected_dir_contents)

        with home_directory_structure() as hds:
            # ACT #
            populator.populate_hds(hds)
            # ASSERT #
            expectation.apply_with_message(self, hds.case_dir,
                                           'contents of home/case dir')

    def test_populate_home_or_sds(self):
        # ARRANGE #
        expected_dir_contents = fs.DirContents([fs.File('a-file-name.txt', 'the file contents')])
        populator = sut.case_home_dir_contents(expected_dir_contents)
        expectation = f_asrt.dir_contains_exactly(expected_dir_contents)

        sds = dummy_sds()
        with home_directory_structure() as hds:
            home_and_sds = HomeAndSds(hds.case_dir, sds)
            # ACT #
            populator.populate_home_or_sds(home_and_sds)
            # ASSERT #
            expectation.apply_with_message(self, hds.case_dir,
                                           'contents of home/case dir')
