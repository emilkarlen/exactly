import unittest

from exactly_lib_test.test_case_utils.file_selectors import parse_file_selector
from exactly_lib_test.test_case_utils.file_selectors import resolvers
from exactly_lib_test.test_case_utils.file_selectors import test_resources_test
from exactly_lib_test.test_case_utils.file_selectors import visitor


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        visitor.suite(),
        resolvers.suite(),
        parse_file_selector.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
