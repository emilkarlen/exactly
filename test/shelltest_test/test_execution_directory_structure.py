__author__ = 'emil'

import unittest
import tempfile
from pathlib import Path

from shelltest import execution_directory_structure


class TestConstruct_execution_directory_structure(unittest.TestCase):
    def test_construct_execution_directory_structure(self):
        with tempfile.TemporaryDirectory(prefix='shelltest-test-') as tmp_dir_name:
            test_root_dir = execution_directory_structure.construct_at(tmp_dir_name)

            root = Path(tmp_dir_name)
            self._assert_exists_dir(test_root_dir.root_dir)

            self._assert_exists_dir(root / 'result' / 'std')
            self._assert_exists_dir(test_root_dir.root_dir)
            self._assert_exists_dir(test_root_dir.result.root_dir)
            self._assert_exists_dir(test_root_dir.result.std.root_dir)

            self._assert_exists_dir(root / 'test')
            self._assert_exists_dir(test_root_dir.test_root_dir)

            self._assert_exists_dir(root / 'testcase')
            self._assert_exists_dir(test_root_dir.test_case_dir)

    def _assert_exists_dir(self, p: Path):
        self.assertTrue(p.exists(), p.name + ' should exist')
        self.assertTrue(p.is_dir(), p.name + ' should be a directory')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestConstruct_execution_directory_structure))
    return ret_val

if __name__ == '__main__':
    unittest.main()
