import unittest

from exactly_lib_test.named_element.file_selector.test_resources_test import file_selector_resolver_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        file_selector_resolver_assertions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
