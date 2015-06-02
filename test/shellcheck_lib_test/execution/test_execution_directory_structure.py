import unittest
import tempfile
from pathlib import Path

from shellcheck_lib.execution import execution_directory_structure


class TestConstructExecutionDirectoryStructure(unittest.TestCase):
    def test_construct_execution_directory_structure(self):
        with tempfile.TemporaryDirectory(prefix='shelltest-test-') as tmp_dir_name:
            eds = execution_directory_structure.construct_at(tmp_dir_name)

            root = Path(tmp_dir_name)
            self._assert_is_existing_dir_with_given_number_of_files_in_it(eds.root_dir,
                                                                          5)

            self._assert_is_existing_empty_dir_with_name(root / 'testcase',
                                                         eds.test_case_dir)

            self._assert_is_existing_empty_dir_with_name(root / 'tmp',
                                                         eds.tmp_dir)

            self._assert_is_existing_empty_dir_with_name(root / 'test',
                                                         eds.test_root_dir)

            self._assert_is_existing_dir_with_given_number_of_files_in_it(eds.result.root_dir,
                                                                          1)
            self._assert_is_existing_empty_dir_with_name(root / 'result' / 'std',
                                                         eds.result.std.root_dir)

            self._assert_is_existing_empty_dir_with_name(root / 'log',
                                                         eds.log_dir)

    def _assert_is_existing_empty_dir_with_name(self,
                                                expected_path: Path,
                                                actual_path: Path):
        self._assert_is_existing_empty_dir(expected_path)
        self.assertEqual(expected_path,
                         actual_path)

    def _assert_is_existing_empty_dir(self, p: Path):
        self._assert_is_existing_dir_with_given_number_of_files_in_it(p, 0)

    def _assert_is_existing_empty_dir(self, p: Path):
        self._assert_exists_dir(p)
        self.assertEquals(
            0,
            len(list(p.iterdir())),
            'The directory is expected to be empty.')

    def _assert_is_existing_dir_with_given_number_of_files_in_it(self,
                                                                 p: Path,
                                                                 expected_number_of_files: int):
        self._assert_exists_dir(p)
        self.assertEquals(
            expected_number_of_files,
            len(list(p.iterdir())),
            'The directory should contain exactly %s files.' % expected_number_of_files)

    def _assert_exists_dir(self, p: Path):
        self.assertTrue(p.exists(), p.name + ' should exist')
        self.assertTrue(p.is_dir(), p.name + ' should be a directory')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestConstructExecutionDirectoryStructure))
    return ret_val


if __name__ == '__main__':
    unittest.main()
