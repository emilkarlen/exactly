import unittest

from exactly_lib_test.test_case_utils.string_matcher.parse import parse_string_matcher


def suite() -> unittest.TestSuite:
    return parse_string_matcher.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
