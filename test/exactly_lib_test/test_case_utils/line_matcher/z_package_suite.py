import unittest

from exactly_lib_test.test_case_utils.line_matcher import line_number, std_expr, model_construction, line_nums_interval
from exactly_lib_test.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib_test.test_case_utils.line_matcher.contents import z_package_suite as contents


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        model_construction.suite(),
        std_expr.suite(),
        line_number.suite(),
        contents.suite(),
        parse_line_matcher.suite(),
        line_nums_interval.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
