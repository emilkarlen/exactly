import unittest

from exactly_lib_test.test_case_utils.logic.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
