import unittest

from exactly_lib_test.test_case_utils.line_matcher import constant, regex, not_, and_, or_, visitor
# from exactly_lib_test.test_case_utils.file_matcher import parse_file_matcher
# from exactly_lib_test.test_case_utils.file_matcher import resolvers
from exactly_lib_test.test_case_utils.line_matcher import test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        visitor.suite(),
        # Visitor (above) is used by the test resources
        test_resources_test.suite(),
        constant.suite(),
        regex.suite(),
        not_.suite(),
        and_.suite(),
        or_.suite(),
        # resolvers.suite(),
        # parse_file_matcher.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
