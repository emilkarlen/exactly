import unittest

from exactly_lib_test.test_case_utils.matcher import parse_integer_matcher


def suite() -> unittest.TestSuite:
    return parse_integer_matcher.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
