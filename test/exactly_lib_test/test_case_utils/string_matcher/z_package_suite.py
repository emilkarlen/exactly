import unittest

from exactly_lib_test.test_case_utils.string_matcher import sdvs
from exactly_lib_test.test_case_utils.string_matcher.parse import z_package_suite as parse


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        sdvs.suite(),
        parse.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
