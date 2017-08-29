import unittest

from exactly_lib_test.test_case_utils.file_selectors.test_resources_test import file_selector_assertions
from exactly_lib_test.test_case_utils.file_selectors.test_resources_test import file_selector_resolver_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        file_selector_assertions.suite(),
        file_selector_resolver_assertions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
