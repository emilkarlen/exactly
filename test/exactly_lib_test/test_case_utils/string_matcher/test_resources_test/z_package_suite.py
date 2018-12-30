import unittest

from exactly_lib_test.test_case_utils.string_matcher.test_resources_test import integration_check, assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        assertions.suite(),
        integration_check.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
