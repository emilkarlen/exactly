import unittest

from exactly_lib_test.test_case_utils.string_matcher.parse import empty, equals, parse_invalid_syntax, \
    parse_with_line_breaks
from exactly_lib_test.test_case_utils.string_matcher.parse.num_lines import z_package_suite as num_lines


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        parse_invalid_syntax.suite(),
        empty.suite(),
        equals.suite(),
        parse_with_line_breaks.suite(),
        num_lines.suite(),
        #    line_matches.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
