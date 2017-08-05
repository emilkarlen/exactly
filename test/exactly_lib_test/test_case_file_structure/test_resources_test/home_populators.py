import unittest

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import RelHomeOptionType
from exactly_lib_test.test_case_file_structure.test_resources import home_populators as sut
from exactly_lib_test.test_case_file_structure.test_resources.hds_utils import home_directory_structure
from exactly_lib_test.test_case_file_structure.test_resources.paths import dummy_sds
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources.value_assertions import file_assertions as f_asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestCaseHomeDirPopulator),
        unittest.makeSuite(TestContentsInDirOfRelHomeOptionType),
        unittest.makeSuite(TestMultiplePopulators),
        unittest.makeSuite(TestEmptyPopulator),
    ])


class TestCaseHomeDirPopulator(unittest.TestCase):
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


class TestContentsInDirOfRelHomeOptionType(unittest.TestCase):
    def test_populate_hds(self):
        # ARRANGE #
        expected_dir_contents = fs.DirContents([fs.File('file-name.txt', 'file contents')])
        populator = sut.contents_in(RelHomeOptionType.REL_HOME,
                                    expected_dir_contents)
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
        populator = sut.contents_in(RelHomeOptionType.REL_HOME,
                                    expected_dir_contents)
        expectation = f_asrt.dir_contains_exactly(expected_dir_contents)

        sds = dummy_sds()
        with home_directory_structure() as hds:
            home_and_sds = HomeAndSds(hds.case_dir, sds)
            # ACT #
            populator.populate_home_or_sds(home_and_sds)
            # ASSERT #
            expectation.apply_with_message(self, hds.case_dir,
                                           'contents of home/case dir')


class TestMultiplePopulators(unittest.TestCase):
    first_file = fs.File('first-file-name.txt', 'contents of first file')
    second_file = fs.File('second-file-name.txt', 'contents of second file')

    def test_two_populators_populate_hds(self):
        # ARRANGE #
        expected_dir_contents = fs.DirContents([self.first_file,
                                                self.second_file])
        first_populator = sut.case_home_dir_contents(fs.DirContents([self.first_file]))
        second_populator = sut.case_home_dir_contents(fs.DirContents([self.second_file]))
        populator = sut.multiple([first_populator,
                                  second_populator])
        expectation = f_asrt.dir_contains_exactly(expected_dir_contents)

        with home_directory_structure() as hds:
            # ACT #
            populator.populate_hds(hds)
            # ASSERT #
            expectation.apply_with_message(self, hds.case_dir,
                                           'contents of home/case dir')

    def test_two_populators_populate_home_or_sds(self):
        # ARRANGE #
        expected_dir_contents = fs.DirContents([self.first_file,
                                                self.second_file])
        first_populator = sut.case_home_dir_contents(fs.DirContents([self.first_file]))
        second_populator = sut.case_home_dir_contents(fs.DirContents([self.second_file]))
        populator = sut.multiple([first_populator,
                                  second_populator])
        expectation = f_asrt.dir_contains_exactly(expected_dir_contents)

        sds = dummy_sds()
        with home_directory_structure() as hds:
            home_and_sds = HomeAndSds(hds.case_dir, sds)
            # ACT #
            populator.populate_home_or_sds(home_and_sds)
            # ASSERT #
            expectation.apply_with_message(self, hds.case_dir,
                                           'contents of home/case dir')

    def test_no_populators_populate_hds(self):
        # ARRANGE #
        expected_dir_contents = fs.DirContents([])
        populator = sut.multiple([])
        expectation = f_asrt.dir_contains_exactly(expected_dir_contents)

        with home_directory_structure() as hds:
            # ACT #
            populator.populate_hds(hds)
            # ASSERT #
            expectation.apply_with_message(self, hds.case_dir,
                                           'contents of home/case dir')


class TestEmptyPopulator(unittest.TestCase):
    def test_populate_hds(self):
        # ARRANGE #
        populator = sut.empty()
        expectation = f_asrt.dir_is_empty()

        with home_directory_structure() as hds:
            # ACT #
            populator.populate_hds(hds)
            # ASSERT #
            expectation.apply_with_message(self, hds.case_dir,
                                           'contents of home/case dir')

    def test_populate_home_or_sds(self):
        # ARRANGE #
        populator = sut.empty()
        expectation = f_asrt.dir_is_empty()

        sds = dummy_sds()
        with home_directory_structure() as hds:
            home_and_sds = HomeAndSds(hds.case_dir, sds)
            # ACT #
            populator.populate_home_or_sds(home_and_sds)
            # ASSERT #
            expectation.apply_with_message(self, hds.case_dir,
                                           'contents of home/case dir')
