import unittest

from exactly_lib_test.util.simple_textstruct import structure
from exactly_lib_test.util.simple_textstruct.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        structure.suite(),
        test_resources_test.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
