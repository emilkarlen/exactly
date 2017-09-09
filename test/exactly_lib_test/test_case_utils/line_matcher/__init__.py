import unittest

from exactly_lib_test.test_case_utils.line_matcher import constant, regex, combinators, visitor
from exactly_lib_test.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib_test.test_case_utils.line_matcher import test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        visitor.suite(),
        # Visitor (above) is used by the test resources
        test_resources_test.suite(),
        constant.suite(),
        regex.suite(),
        combinators.suite(),
        parse_line_matcher.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
