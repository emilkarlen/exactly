import unittest

from exactly_lib_test.impls.types.files_source import reference, copy_dir_contents
from exactly_lib_test.impls.types.files_source.literal import z_package_suite as literal


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        reference.suite(),
        copy_dir_contents.suite(),
        literal.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
