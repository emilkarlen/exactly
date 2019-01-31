import unittest

from exactly_lib_test.test_case_utils.line_matcher.test_resources_test import value_assertions, resolver_assertions, \
    integration_check


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        value_assertions.suite(),
        resolver_assertions.suite(),
        integration_check.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
