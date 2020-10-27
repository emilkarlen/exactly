import unittest

from exactly_lib_test.test_case_utils.matcher import constant, combinator_matchers, comparison_matcher


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        constant.suite(),
        combinator_matchers.suite(),
        comparison_matcher.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
