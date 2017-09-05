import unittest

from exactly_lib_test.test_case_utils.line_matcher import regex, visitor
# from exactly_lib_test.test_case_utils.file_matcher import parse_file_matcher
# from exactly_lib_test.test_case_utils.file_matcher import resolvers
from exactly_lib_test.test_case_utils.line_matcher import test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        regex.suite(),
        visitor.suite(),
        # resolvers.suite(),
        # parse_file_matcher.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
