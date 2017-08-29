import unittest

from exactly_lib_test.test_case_utils.lines_transformers.test_resources_test import resolver_assertions
from exactly_lib_test.test_case_utils.lines_transformers.test_resources_test import value_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        value_assertions.suite(),
        resolver_assertions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
