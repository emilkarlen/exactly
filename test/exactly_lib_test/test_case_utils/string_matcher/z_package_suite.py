import unittest

from exactly_lib_test.test_case_utils.string_matcher import empty, equals, matches_regex, multiple_transformations, \
    on_transformed, parse_invalid_syntax, parse_with_line_breaks, std_expr
from exactly_lib_test.test_case_utils.string_matcher.num_lines import z_package_suite as num_lines
from exactly_lib_test.test_case_utils.string_matcher.quant_over_lines import z_package_suite as line_matches


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        parse_invalid_syntax.suite(),
        std_expr.suite(),
        empty.suite(),
        equals.suite(),
        parse_with_line_breaks.suite(),
        num_lines.suite(),
        line_matches.suite(),
        matches_regex.suite(),
        on_transformed.suite(),
        multiple_transformations.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
