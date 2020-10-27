import unittest

from exactly_lib_test.test_case_utils.matcher import constant, combinator_matchers


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        constant.suite(),
        combinator_matchers.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
