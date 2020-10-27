import unittest

from exactly_lib_test.test_case_utils.string_transformers.filter.line_matcher import z_package_suite as line_matcher
from exactly_lib_test.test_case_utils.string_transformers.filter.line_numbers import \
    z_package_suite as line_numbers


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        line_matcher.suite(),
        line_numbers.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
