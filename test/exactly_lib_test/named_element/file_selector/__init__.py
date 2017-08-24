import unittest

from exactly_lib_test.named_element.file_selector import file_selector_constant


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        file_selector_constant.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
