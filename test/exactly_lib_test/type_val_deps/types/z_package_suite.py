import unittest

from exactly_lib_test.type_val_deps.types.list_ import z_package_suite as list_
from exactly_lib_test.type_val_deps.types.path import z_package_suite as path
from exactly_lib_test.type_val_deps.types.string_ import z_package_suite as string
from exactly_lib_test.type_val_deps.types.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        string.suite(),
        path.suite(),
        list_.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
