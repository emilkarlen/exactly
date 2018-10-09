import unittest
from pathlib import Path

from exactly_lib.util import file_utils as sut
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir
from exactly_lib_test.test_resources.name_and_value import NameAndValue


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestTmpDirFileSpaceAsDirCreatedOnDemand)


class TestTmpDirFileSpaceAsDirCreatedOnDemand(unittest.TestCase):
    def test_non_existing_root_dir_SHOULD_not_be_created_when_object_is_constructed(self):
        # ARRANGE #
        with tmp_dir() as existing_dir_path:
            space_root_dir = existing_dir_path / 'non-existing-root'
            # ACT #
            sut.TmpDirFileSpaceAsDirCreatedOnDemand(space_root_dir)
            # ASSERT #
            self.assertFalse(space_root_dir.exists())

    def test_non_existing_root_dir_SHOULD_be_created_when_file_is_demanded(self):
        # ARRANGE #
        with tmp_dir() as existing_dir_path:
            space_root_dir = existing_dir_path / 'non-existing-root-comp-1' / 'comp-2'
            # ACT
            space = sut.TmpDirFileSpaceAsDirCreatedOnDemand(space_root_dir)
            space.new_path()
            # ASSERT #
            self.assertTrue(space_root_dir.is_dir())

    def test_existing_root_dir_SHOULD_not_be_created_when_file_is_demanded(self):
        # ARRANGE #
        with tmp_dir() as existing_dir_path:
            space_root_dir = existing_dir_path
            # ACT
            space = sut.TmpDirFileSpaceAsDirCreatedOnDemand(space_root_dir)
            space.new_path()
            # ASSERT #
            self.assertTrue(space_root_dir.is_dir())

    def test_demanded_files_SHOULD_be_sequence_of_increasing_numbers__non_existing_root_dir(self):
        # ARRANGE #
        cases = [
            NameAndValue('existing root dir',
                         lambda existing_dir: existing_dir
                         ),
            NameAndValue('non existing root dir',
                         lambda existing_dir: existing_dir / 'non-existing-root-dir-component'
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                with tmp_dir() as existing_dir_path:
                    space_root_dir = case.value(existing_dir_path)
                    # ACT
                    space = sut.TmpDirFileSpaceAsDirCreatedOnDemand(space_root_dir)
                    file_1 = space.new_path()
                    file_2 = space.new_path()
                    # ASSERT #
                    self._assert_is_non_existing_file(space_root_dir / '01',
                                                      file_1)
                    self._assert_is_non_existing_file(space_root_dir / '02',
                                                      file_2)
                    self._assert_num_files_in_dir(space_root_dir,
                                                  expected_number_of_files=0)

    def test_new_path_as_existing_dir(self):
        # ARRANGE #
        cases = [
            NameAndValue('existing root dir',
                         lambda existing_dir: existing_dir
                         ),
            NameAndValue('non existing root dir',
                         lambda existing_dir: existing_dir / 'non-existing-root-dir-component'
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                with tmp_dir() as existing_dir_path:
                    space_root_dir = case.value(existing_dir_path)
                    # ACT
                    space = sut.TmpDirFileSpaceAsDirCreatedOnDemand(space_root_dir)
                    file_1 = space.new_path()
                    dir_2 = space.new_path_as_existing_dir()
                    file_3 = space.new_path()
                    dir_4 = space.new_path_as_existing_dir()
                    # ASSERT #
                    self._assert_is_non_existing_file(space_root_dir / '01',
                                                      file_1)
                    self._assert_is_existing_dir(space_root_dir / '02',
                                                 dir_2)
                    self._assert_is_non_existing_file(space_root_dir / '03',
                                                      file_3)
                    self._assert_is_existing_dir(space_root_dir / '04',
                                                 dir_4)
                    self._assert_num_files_in_dir(space_root_dir,
                                                  expected_number_of_files=2)

    def _assert_is_non_existing_file(self,
                                     expected: Path,
                                     actual: Path):
        self.assertEqual(expected,
                         actual)
        self.assertFalse(actual.exists())

    def _assert_is_existing_dir(self,
                                expected: Path,
                                actual: Path):
        self.assertEqual(expected,
                         actual)
        self.assertTrue(actual.is_dir())

    def _assert_num_files_in_dir(self,
                                 dir_path: Path,
                                 expected_number_of_files: int):
        existing_files_in_space_dir = list(dir_path.iterdir())
        self.assertEqual(expected_number_of_files, len(existing_files_in_space_dir))
