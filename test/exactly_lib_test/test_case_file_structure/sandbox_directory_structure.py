import tempfile
import unittest
from pathlib import Path

from exactly_lib import program_info
from exactly_lib.test_case_file_structure import sandbox_directory_structure
from exactly_lib.util.file_utils.misc_utils import resolved_path


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestConstructExecutionDirectoryStructure)


class TestConstructExecutionDirectoryStructure(unittest.TestCase):
    def test_construct_sandbox_directory_structure(self):
        with tempfile.TemporaryDirectory(prefix=program_info.PROGRAM_NAME + '-test-') as tmp_dir_name:
            root = resolved_path(tmp_dir_name)
            tmp_dir_name = str(root)
            sds = sandbox_directory_structure.construct_at(tmp_dir_name)

            self._assert_is_existing_dir_with_given_number_of_files_in_it(sds.root_dir,
                                                                          4)

            self._assert_is_existing_empty_dir_with_name(root / 'tmp',
                                                         sds.user_tmp_dir)

            self._assert_is_existing_empty_dir_with_name(root / 'act',
                                                         sds.act_dir)

            self._assert_is_existing_empty_dir_with_name(root / 'result',
                                                         sds.result_dir)

            self._assert_is_existing_dir_with_given_number_of_files_in_it(root / 'internal',
                                                                          2)

            self._assert_is_existing_empty_dir_with_name(root / 'internal' / 'tmp',
                                                         sds.internal_tmp_dir)

            self._assert_is_existing_empty_dir_with_name(root / 'internal' / 'log',
                                                         sds.log_dir)

    def _assert_is_existing_empty_dir_with_name(self,
                                                expected_path: Path,
                                                actual_path: Path):
        self._assert_is_existing_empty_dir(expected_path)
        self.assertEqual(expected_path,
                         actual_path)

    def _assert_is_existing_empty_dir(self, p: Path):
        self._assert_is_existing_dir_with_given_number_of_files_in_it(p, 0)

    def _assert_is_existing_dir_with_given_number_of_files_in_it(self,
                                                                 p: Path,
                                                                 expected_number_of_files: int):
        self._assert_exists_dir(p)
        self.assertEqual(
            expected_number_of_files,
            len(list(p.iterdir())),
            'The directory should contain exactly %s files.' % expected_number_of_files)

    def _assert_exists_dir(self, p: Path):
        self.assertTrue(p.exists(), p.name + ' should exist')
        self.assertTrue(p.is_dir(), p.name + ' should be a directory')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
