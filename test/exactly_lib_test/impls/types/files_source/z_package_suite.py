import unittest

from exactly_lib_test.impls.types.files_source import reference, copy_dir_contents
from exactly_lib_test.impls.types.files_source.file_list import z_package_suite as file_list


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        reference.suite(),
        copy_dir_contents.suite(),
        file_list.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
