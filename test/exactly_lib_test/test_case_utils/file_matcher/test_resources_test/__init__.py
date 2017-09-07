import unittest

from exactly_lib_test.test_case_utils.file_matcher.test_resources_test import value_assertions
from exactly_lib_test.test_case_utils.file_matcher.test_resources_test import resolver_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        value_assertions.suite(),
        resolver_assertions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
