import unittest

from exactly_lib_test.named_element.file_selector import \
    test_resources_test, \
    file_selector_constant


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        file_selector_constant.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
