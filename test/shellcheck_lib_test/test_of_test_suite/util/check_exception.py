import pathlib
import tempfile
import unittest

from shellcheck_lib.test_suite.suite_hierarchy_reading import read

from shellcheck_lib_test.util.file_structure import DirContents


class Setup:
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError()

    def file_structure_to_read(self) -> DirContents:
        raise NotImplementedError()

    def expected_exception_class(self):
        raise NotImplementedError()

    def check_exception(self,
                        root_path: pathlib.Path,
                        actual: Exception,
                        put: unittest.TestCase):
        raise NotImplementedError()


def check(setup: Setup,
          put: unittest.TestCase):
    with tempfile.TemporaryDirectory(prefix='shellcheck-test-') as tmp_dir:
        tmp_dir_path = pathlib.Path(tmp_dir)
        setup.file_structure_to_read().write_to(tmp_dir_path)
        with put.assertRaises(Exception) as cm:
            read(setup.root_suite_based_at(tmp_dir_path))
        setup.check_exception(tmp_dir_path, cm.exception, put)
