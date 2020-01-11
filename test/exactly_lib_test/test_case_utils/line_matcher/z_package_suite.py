import unittest

from exactly_lib_test.test_case_utils.line_matcher import line_number, regex, std_expr
from exactly_lib_test.test_case_utils.line_matcher import model_construction
from exactly_lib_test.test_case_utils.line_matcher import parse_line_matcher


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        model_construction.suite(),
        std_expr.suite(),
        line_number.suite(),
        regex.suite(),
        parse_line_matcher.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
