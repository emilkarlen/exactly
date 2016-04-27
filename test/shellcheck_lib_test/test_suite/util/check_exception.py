import pathlib
import tempfile
import unittest

from exactly_lib import program_info
from exactly_lib.test_suite.suite_hierarchy_reading import Reader, default_environment
from exactly_lib.util.file_utils import resolved_path
from shellcheck_lib_test.test_resources.file_structure import DirContents


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
    with tempfile.TemporaryDirectory(prefix=program_info.PROGRAM_NAME + '-test-') as tmp_dir:
        tmp_dir_path = resolved_path(tmp_dir)
        setup.file_structure_to_read().write_to(tmp_dir_path)
        with put.assertRaises(Exception) as cm:
            Reader(default_environment()).apply(setup.root_suite_based_at(tmp_dir_path))
        setup.check_exception(tmp_dir_path, cm.exception, put)
