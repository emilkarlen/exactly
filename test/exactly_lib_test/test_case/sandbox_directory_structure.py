import tempfile
import unittest
from pathlib import Path

from exactly_lib import program_info
from exactly_lib.test_case import sandbox_directory_structure
from exactly_lib.util.file_utils import resolved_path
from exactly_lib_test.test_resources.assertions.file_checks import FileChecker


class TestConstructExecutionDirectoryStructure(unittest.TestCase):
    def test_construct_sandbox_directory_structure(self):
        with tempfile.TemporaryDirectory(prefix=program_info.PROGRAM_NAME + '-test-') as tmp_dir_name:
            root = resolved_path(tmp_dir_name)
            tmp_dir_name = str(root)
            sds = sandbox_directory_structure.construct_at(tmp_dir_name)

            self._assert_is_existing_dir_with_given_number_of_files_in_it(sds.root_dir,
                                                                          5)

            self._assert_is_existing_empty_dir_with_name(root / 'testcase',
                                                         sds.test_case_dir)

            self._assert_is_existing_dir_with_given_number_of_files_in_it(root / 'tmp',
                                                                          2)

            self._assert_is_existing_empty_dir_with_name(root / 'tmp' / 'internal',
                                                         sds.tmp.internal_dir)

            self._assert_is_existing_empty_dir_with_name(root / 'tmp' / 'user',
                                                         sds.tmp.user_dir)

            self._assert_is_existing_empty_dir_with_name(root / 'testcase',
                                                         sds.test_case_dir)

            self._assert_is_existing_empty_dir_with_name(root / 'act',
                                                         sds.act_dir)

            self._assert_is_existing_empty_dir_with_name(root / 'result',
                                                         sds.result.root_dir)

            self._assert_is_existing_empty_dir_with_name(root / 'log',
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
        self.assertEquals(
            expected_number_of_files,
            len(list(p.iterdir())),
            'The directory should contain exactly %s files.' % expected_number_of_files)

    def _assert_exists_dir(self, p: Path):
        self.assertTrue(p.exists(), p.name + ' should exist')
        self.assertTrue(p.is_dir(), p.name + ' should be a directory')


def is_sandbox_directory_structure_after_execution(fc: FileChecker,
                                                   root_dir_name: str):
    sds = sandbox_directory_structure.SandboxDirectoryStructure(root_dir_name)
    fc.assert_exists_dir_with_given_number_of_files_in_it(sds.root_dir,
                                                          5)
    fc.assert_exists_dir(sds.test_case_dir)
    fc.assert_exists_dir(sds.tmp.root_dir)
    fc.assert_exists_dir(sds.tmp.internal_dir)
    fc.assert_exists_dir(sds.tmp.user_dir)
    fc.assert_exists_dir(sds.act_dir)

    fc.assert_exists_dir_with_given_number_of_files_in_it(sds.result.root_dir,
                                                          3)
    fc.assert_exists_plain_file(sds.result.exitcode_file)
    fc.assert_exists_plain_file(sds.result.stdout_file)
    fc.assert_exists_plain_file(sds.result.stderr_file)

    fc.assert_exists_dir(sds.log_dir)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestConstructExecutionDirectoryStructure))
    return ret_val


if __name__ == '__main__':
    unittest.main()
