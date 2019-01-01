import unittest

from exactly_lib_test.test_case_utils.string_matcher.parse import empty, equals, parse_invalid_syntax, \
    parse_with_line_breaks, symbol_reference, multiple_transformations
from exactly_lib_test.test_case_utils.string_matcher.parse.line_matches import z_package_suite as line_matches
from exactly_lib_test.test_case_utils.string_matcher.parse.num_lines import z_package_suite as num_lines


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        parse_invalid_syntax.suite(),
        empty.suite(),
        equals.suite(),
        parse_with_line_breaks.suite(),
        num_lines.suite(),
        line_matches.suite(),
        symbol_reference.suite(),
        multiple_transformations.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
