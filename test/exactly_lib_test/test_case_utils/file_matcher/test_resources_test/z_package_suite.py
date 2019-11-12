import unittest

from exactly_lib_test.test_case_utils.file_matcher.test_resources_test import ddv_assertions, integration_check
from exactly_lib_test.test_case_utils.file_matcher.test_resources_test import resolver_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        ddv_assertions.suite(),
        resolver_assertions.suite(),
        integration_check.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
