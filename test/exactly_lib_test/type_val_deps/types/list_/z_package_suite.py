import unittest

from exactly_lib_test.type_val_deps.types.list_ import list_sdv, list_ddv
from exactly_lib_test.type_val_deps.types.list_.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        list_ddv.suite(),
        list_sdv.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
