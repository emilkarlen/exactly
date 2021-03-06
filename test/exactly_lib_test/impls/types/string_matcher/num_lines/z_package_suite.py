import unittest

from exactly_lib_test.impls.types.string_matcher.num_lines import \
    invalid_syntax_test_cases, operand_expression_test_cases, valid_syntax_test_cases


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        invalid_syntax_test_cases.suite(),
        valid_syntax_test_cases.suite(),
        operand_expression_test_cases.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
