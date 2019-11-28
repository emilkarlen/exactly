import unittest

from exactly_lib_test.test_case_utils.matcher import constant
from exactly_lib_test.test_case_utils.matcher import parse_integer_matcher
from exactly_lib_test.test_case_utils.matcher.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        constant.suite(),
        parse_integer_matcher.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
