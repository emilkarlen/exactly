import unittest

from exactly_lib_test.type_val_deps.data.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    return test_resources_test.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
