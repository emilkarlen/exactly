import unittest

from exactly_lib_test.test_case_utils.file_matcher.test_resources_test import integration_check
from exactly_lib_test.test_case_utils.file_matcher.test_resources_test import sdv_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        sdv_assertions.suite(),
        integration_check.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
