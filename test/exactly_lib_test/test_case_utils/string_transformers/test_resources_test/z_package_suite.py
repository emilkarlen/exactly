import unittest

from exactly_lib_test.test_case_utils.string_transformers.test_resources_test import \
    resolver_assertions, test_transformers, value_assertions, integration_check


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        value_assertions.suite(),
        resolver_assertions.suite(),
        test_transformers.suite(),
        integration_check.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
