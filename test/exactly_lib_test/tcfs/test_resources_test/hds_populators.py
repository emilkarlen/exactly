import unittest

from exactly_lib.tcfs.path_relativity import RelHdsOptionType
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib_test.tcfs.test_resources import hds_populators as sut
from exactly_lib_test.tcfs.test_resources.fake_ds import fake_sds
from exactly_lib_test.tcfs.test_resources.hds_utils import home_directory_structure
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.value_assertions import file_assertions as f_asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestCaseHdsDirPopulator),
        unittest.makeSuite(TestContentsInDirOfRelHdsOptionType),
        unittest.makeSuite(TestMultiplePopulators),
        unittest.makeSuite(TestEmptyPopulator),
    ])


class TestCaseHdsDirPopulator(unittest.TestCase):
    def test_populate_hds(self):
        # ARRANGE #
        expected_dir_contents = fs.DirContents([fs.File('file-name.txt', 'file contents')])
        populator = sut.hds_case_dir_contents(expected_dir_contents)
        expectation = f_asrt.dir_contains_exactly(expected_dir_contents)

        with home_directory_structure() as hds:
            # ACT #
            populator.populate_hds(hds)
            # ASSERT #
            expectation.apply_with_message(self, hds.case_dir,
                                           'contents of HDS/case dir')

    def test_populate_hds_or_sds(self):
        # ARRANGE #
        expected_dir_contents = fs.DirContents([fs.File('a-file-name.txt', 'the file contents')])
        populator = sut.hds_case_dir_contents(expected_dir_contents)
        expectation = f_asrt.dir_contains_exactly(expected_dir_contents)

        sds = fake_sds()
        with home_directory_structure() as hds:
            tcds = TestCaseDs(hds, sds)
            # ACT #
            populator.populate_tcds(tcds)
            # ASSERT #
            expectation.apply_with_message(self, hds.case_dir,
                                           'contents of HDS/case dir')


class TestContentsInDirOfRelHdsOptionType(unittest.TestCase):
    def test_populate_hds(self):
        # ARRANGE #
        expected_dir_contents = fs.DirContents([fs.File('file-name.txt', 'file contents')])
        populator = sut.contents_in(RelHdsOptionType.REL_HDS_CASE,
                                    expected_dir_contents)
        expectation = f_asrt.dir_contains_exactly(expected_dir_contents)

        with home_directory_structure() as hds:
            # ACT #
            populator.populate_hds(hds)
            # ASSERT #
            expectation.apply_with_message(self, hds.case_dir,
                                           'contents of HDS/case dir')

    def test_populate_tcds(self):
        # ARRANGE #
        expected_dir_contents = fs.DirContents([fs.File('a-file-name.txt', 'the file contents')])
        populator = sut.contents_in(RelHdsOptionType.REL_HDS_CASE,
                                    expected_dir_contents)
        expectation = f_asrt.dir_contains_exactly(expected_dir_contents)

        sds = fake_sds()
        with home_directory_structure() as hds:
            tcds = TestCaseDs(hds, sds)
            # ACT #
            populator.populate_tcds(tcds)
            # ASSERT #
            expectation.apply_with_message(self, hds.case_dir,
                                           'contents of HDS/case dir')


class TestMultiplePopulators(unittest.TestCase):
    first_file = fs.File('first-file-name.txt', 'contents of first file')
    second_file = fs.File('second-file-name.txt', 'contents of second file')

    def test_two_populators_populate_hds(self):
        # ARRANGE #
        expected_dir_contents = fs.DirContents([self.first_file,
                                                self.second_file])
        first_populator = sut.hds_case_dir_contents(fs.DirContents([self.first_file]))
        second_populator = sut.hds_case_dir_contents(fs.DirContents([self.second_file]))
        populator = sut.multiple([first_populator,
                                  second_populator])
        expectation = f_asrt.dir_contains_exactly(expected_dir_contents)

        with home_directory_structure() as hds:
            # ACT #
            populator.populate_hds(hds)
            # ASSERT #
            expectation.apply_with_message(self, hds.case_dir,
                                           'contents of HDS/case dir')

    def test_two_populators_populate_tcds(self):
        # ARRANGE #
        expected_dir_contents = fs.DirContents([self.first_file,
                                                self.second_file])
        first_populator = sut.hds_case_dir_contents(fs.DirContents([self.first_file]))
        second_populator = sut.hds_case_dir_contents(fs.DirContents([self.second_file]))
        populator = sut.multiple([first_populator,
                                  second_populator])
        expectation = f_asrt.dir_contains_exactly(expected_dir_contents)

        sds = fake_sds()
        with home_directory_structure() as hds:
            tcds = TestCaseDs(hds, sds)
            # ACT #
            populator.populate_tcds(tcds)
            # ASSERT #
            expectation.apply_with_message(self, hds.case_dir,
                                           'contents of HDS/case dir')

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
                                           'contents of HDS/case dir')


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
                                           'contents of HDS/case dir')

    def test_populate_tcds(self):
        # ARRANGE #
        populator = sut.empty()
        expectation = f_asrt.dir_is_empty()

        sds = fake_sds()
        with home_directory_structure() as hds:
            tcds = TestCaseDs(hds, sds)
            # ACT #
            populator.populate_tcds(tcds)
            # ASSERT #
            expectation.apply_with_message(self, hds.case_dir,
                                           'contents of HDS/case dir')
