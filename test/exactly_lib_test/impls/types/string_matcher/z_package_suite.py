import unittest

from exactly_lib_test.impls.types.string_matcher import empty, equals, matches_regex, multiple_transformations, \
    on_transformed, parse_invalid_syntax, parse_with_line_breaks, std_expr, infix_op_freezing
from exactly_lib_test.impls.types.string_matcher.num_lines import z_package_suite as num_lines
from exactly_lib_test.impls.types.string_matcher.quant_over_lines import z_package_suite as line_matches
from exactly_lib_test.impls.types.string_matcher.run_program import z_package_suite as run_program


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        parse_invalid_syntax.suite(),
        std_expr.suite(),
        infix_op_freezing.suite(),
        empty.suite(),
        equals.suite(),
        parse_with_line_breaks.suite(),
        num_lines.suite(),
        line_matches.suite(),
        matches_regex.suite(),
        on_transformed.suite(),
        multiple_transformations.suite(),
        run_program.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
