import os
import pathlib
import tempfile
import unittest

from exactly_lib import program_info
from exactly_lib.test_suite.file_reading.suite_hierarchy_reading import Reader
from exactly_lib.util.file_utils.misc_utils import resolved_path, preserved_cwd
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.test_suite.test_resources.environment import default_environment


class Setup:
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError()

    def file_structure_to_read(self) -> DirContents:
        raise NotImplementedError()

    def check_exception(self,
                        root_path: pathlib.Path,
                        actual: Exception,
                        put: unittest.TestCase):
        raise NotImplementedError()


def check(setup: Setup,
          put: unittest.TestCase):
    # ARRANGE #
    with tempfile.TemporaryDirectory(prefix=program_info.PROGRAM_NAME + '-test-') as tmp_dir:
        with preserved_cwd():
            tmp_dir_path = resolved_path(tmp_dir)
            os.chdir(str(tmp_dir_path))

            setup.file_structure_to_read().write_to(tmp_dir_path)
            # ACT & ASSERT #
            with put.assertRaises(Exception) as cm:
                # ACT #
                Reader(default_environment()).apply(setup.root_suite_based_at(tmp_dir_path))
            # ASSERT #
            setup.check_exception(tmp_dir_path, cm.exception, put)
