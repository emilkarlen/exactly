import unittest
from pathlib import Path
from typing import Callable, Sequence

from exactly_lib.util.file_utils import tmp_file_spaces as sut
from exactly_lib.util.file_utils.tmp_file_spaces import FileNamesConfig
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestTmpDirFileSpaceAsDirCreatedOnDemand)


class TestTmpDirFileSpaceAsDirCreatedOnDemand(unittest.TestCase):
    def test_non_existing_root_dir_SHOULD_not_be_created_when_object_is_constructed(self):
        # ARRANGE #
        with tmp_dir() as existing_dir_path:
            space_root_dir = existing_dir_path / 'non-existing-root'
            # ACT #
            sut.TmpDirFileSpaceAsDirCreatedOnDemand(space_root_dir,
                                                    FileNamesConfig(iter([]),
                                                                    iter([])),
                                                    )
            # ASSERT #
            self.assertFalse(space_root_dir.exists())

    def test_non_existing_root_dir_SHOULD_be_created_when_file_is_demanded(self):
        # ARRANGE #
        with tmp_dir() as existing_dir_path:
            space_root_dir = existing_dir_path / 'non-existing-root-comp-1' / 'comp-2'
            # ACT
            space = sut.TmpDirFileSpaceAsDirCreatedOnDemand(space_root_dir,
                                                            FileNamesConfig(iter(['name']),
                                                                            iter([])),
                                                            )
            space.new_path()
            # ASSERT #
            self.assertTrue(space_root_dir.is_dir())

    def test_existing_root_dir_SHOULD_not_be_created_when_file_is_demanded(self):
        # ARRANGE #
        with tmp_dir() as existing_dir_path:
            space_root_dir = existing_dir_path
            # ACT
            space = sut.TmpDirFileSpaceAsDirCreatedOnDemand(space_root_dir,
                                                            FileNamesConfig(iter(['name']),
                                                                            iter([])),
                                                            )
            space.new_path()
            # ASSERT #
            self.assertTrue(space_root_dir.is_dir())

    def test_demanded_files_in_root_dir_SHOULD_be_that_of_iterator__non_existing_root_dir(self):
        # ARRANGE #
        for case in _root_dir_cases():
            with self.subTest(case.name):
                with tmp_dir() as existing_dir_path:
                    space_root_dir = case.value(existing_dir_path)
                    # ACT
                    space = sut.TmpDirFileSpaceAsDirCreatedOnDemand(space_root_dir,
                                                                    FileNamesConfig(iter(['a', 'b']),
                                                                                    iter([])),
                                                                    )
                    file_1 = space.new_path()
                    file_2 = space.new_path()
                    # ASSERT #
                    self._assert_is_non_existing_file(space_root_dir / 'a',
                                                      file_1)
                    self._assert_is_non_existing_file(space_root_dir / 'b',
                                                      file_2)
                    self._assert_num_files_in_dir(space_root_dir,
                                                  expected_number_of_files=0)

    def test_sub_dir_space(self):
        # ARRANGE #
        for case in _root_dir_cases():
            with self.subTest(case.name):
                with tmp_dir() as existing_dir_path:
                    space_root_dir = case.value(existing_dir_path)
                    root_space = sut.TmpDirFileSpaceAsDirCreatedOnDemand(space_root_dir,
                                                                         FileNamesConfig(
                                                                             iter(['a', 'b']),
                                                                             iter([
                                                                                 iter(['1', '2'])
                                                                             ])
                                                                         ),
                                                                         )
                    # AC & ASSERT #

                    sub_dir_space = root_space.sub_dir_space()

                    self.assertTrue(space_root_dir.is_dir(),
                                    'Root space dir should be created when sub space is created')

                    actual_sub_space_path_1 = sub_dir_space.new_path()

                    expected_sub_space_root_dir = space_root_dir / 'a'
                    expected_sub_space_file_1 = expected_sub_space_root_dir / '1'

                    self.assertTrue(expected_sub_space_root_dir.is_dir())
                    self._assert_num_files_in_dir(
                        expected_sub_space_root_dir,
                        expected_number_of_files=0,
                        msg='Sub dir root dir should be empty'
                    )

                    self.assertEqual(actual_sub_space_path_1,
                                     expected_sub_space_file_1)

                    root_file_2 = root_space.new_path()
                    actual_sub_space_path_2 = sub_dir_space.new_path_as_existing_dir()

                    self._assert_is_non_existing_file(space_root_dir / 'b',
                                                      root_file_2)
                    self._assert_is_existing_dir(expected_sub_space_root_dir / '2',
                                                 actual_sub_space_path_2)
                    self._assert_num_files_in_dir(space_root_dir,
                                                  expected_number_of_files=1)
                    self._assert_num_files_in_dir(expected_sub_space_root_dir,
                                                  expected_number_of_files=1)

    def test_new_path_as_existing_dir(self):
        # ARRANGE #
        for case in _root_dir_cases():
            with self.subTest(case.name):
                with tmp_dir() as existing_dir_path:
                    space_root_dir = case.value(existing_dir_path)
                    # ACT
                    space = sut.TmpDirFileSpaceAsDirCreatedOnDemand(space_root_dir,
                                                                    FileNamesConfig(
                                                                        iter(['1', '2', '3', '4']),
                                                                        iter([])
                                                                    ),
                                                                    )
                    file_1 = space.new_path()
                    dir_2 = space.new_path_as_existing_dir()
                    file_3 = space.new_path()
                    dir_4 = space.new_path_as_existing_dir()
                    # ASSERT #
                    self._assert_is_non_existing_file(space_root_dir / '1',
                                                      file_1)
                    self._assert_is_existing_dir(space_root_dir / '2',
                                                 dir_2)
                    self._assert_is_non_existing_file(space_root_dir / '3',
                                                      file_3)
                    self._assert_is_existing_dir(space_root_dir / '4',
                                                 dir_4)
                    self._assert_num_files_in_dir(space_root_dir,
                                                  expected_number_of_files=2)

    def test_sub_dir_spaces_SHOULD_use_names_from_consecutive_name_iterators(self):
        # ARRANGE #
        for case in _root_dir_cases():
            with self.subTest(case.name):
                with tmp_dir() as existing_dir_path:
                    space_root_dir = case.value(existing_dir_path)
                    root_space = sut.TmpDirFileSpaceAsDirCreatedOnDemand(space_root_dir,
                                                                         FileNamesConfig(
                                                                             iter(['a', 'b']),
                                                                             iter([
                                                                                 iter(['1', '2']),
                                                                                 iter(['10', '20']),
                                                                             ])
                                                                         ),
                                                                         )
                    # AC & ASSERT #

                    sub_dir_space_1 = root_space.sub_dir_space()
                    sub_dir_space_2 = root_space.sub_dir_space()

                    path_1_1 = sub_dir_space_1.new_path()
                    path_1_2 = sub_dir_space_1.new_path()

                    path_2_1 = sub_dir_space_2.new_path()
                    path_2_2 = sub_dir_space_2.new_path()

                    self.assertEqual(
                        space_root_dir / 'a' / '1',
                        path_1_1,
                    )
                    self.assertEqual(
                        space_root_dir / 'a' / '2',
                        path_1_2,
                    )

                    self.assertEqual(
                        space_root_dir / 'b' / '10',
                        path_2_1,
                    )
                    self.assertEqual(
                        space_root_dir / 'b' / '20',
                        path_2_2,
                    )

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
                                 expected_number_of_files: int,
                                 msg: str = ''):
        existing_files_in_space_dir = list(dir_path.iterdir())
        self.assertEqual(len(existing_files_in_space_dir),
                         expected_number_of_files,
                         msg)


def _root_dir_cases() -> Sequence[NameAndValue[Callable[[Path], Path]]]:
    return [
        NameAndValue('existing root dir',
                     lambda existing_dir: existing_dir
                     ),
        NameAndValue('non existing root dir',
                     lambda existing_dir: existing_dir / 'non-existing-root-dir-component'
                     ),
    ]
