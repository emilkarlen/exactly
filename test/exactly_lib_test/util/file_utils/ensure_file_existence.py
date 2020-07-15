import unittest

from exactly_lib.util.file_utils import ensure_file_existence as sut
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_resources.files import tmp_dir
from exactly_lib_test.test_resources.files.file_structure import DirContents, File, Dir


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestEnsureDirectoryExists)


class TestEnsureDirectoryExists(unittest.TestCase):
    def test_fail(self):
        # ARRANGE #
        regular_file = File.empty('regular-file')
        cwd_contents = DirContents([
            regular_file
        ])
        cases = [
            NameAndValue(
                'existing regular file',
                regular_file.name_as_path,
            ),
            NameAndValue(
                'middle component that is existing regular file',
                regular_file.name_as_path / 'non-existing',
            ),
        ]
        with tmp_dir.tmp_dir_as_cwd(cwd_contents):
            for case in cases:
                with self.subTest(case.name):
                    with self.assertRaises(OSError):
                        # ACT & ASSERT #
                        sut.ensure_directory_exists(case.value)

    def test_succeed(self):
        # ARRANGE #
        existing_dir = Dir.empty('a-dir')
        cwd_contents = DirContents([
            existing_dir
        ])
        cases = [
            NameAndValue(
                'existing dir',
                existing_dir.name_as_path,
            ),
            NameAndValue(
                'non-existing dir',
                existing_dir.name_as_path / 'non-existing',
            ),
            NameAndValue(
                'non-existing dir / multiple non-existing path components',
                existing_dir.name_as_path / 'non-existing-1' / 'non-existing-2',
            ),
        ]
        with tmp_dir.tmp_dir_as_cwd(cwd_contents):
            for case in cases:
                with self.subTest(case.name):
                    path = case.value
                    # ACT #
                    sut.ensure_directory_exists(path)
                    # ASSERT #
                    self.assertTrue(path.is_dir())
