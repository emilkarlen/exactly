import unittest

from exactly_lib_test.test_case_utils.integer_matcher import specific
from exactly_lib_test.test_case_utils.integer_matcher import std_expr


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        std_expr.suite(),
        specific.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
