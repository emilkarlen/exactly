import unittest

from exactly_lib_test.named_element import parse_file_selector


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        parse_file_selector.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
