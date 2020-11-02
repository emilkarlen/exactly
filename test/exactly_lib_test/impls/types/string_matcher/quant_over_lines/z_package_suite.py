import unittest

from exactly_lib_test.impls.types.string_matcher.quant_over_lines import \
    common_test_cases, valid_syntax_test_cases__any
from exactly_lib_test.impls.types.string_matcher.quant_over_lines import valid_syntax_test_cases__every


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        common_test_cases.suite(),
        valid_syntax_test_cases__any.suite(),
        valid_syntax_test_cases__every.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
