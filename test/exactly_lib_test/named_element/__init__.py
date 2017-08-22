import unittest

from exactly_lib_test.named_element import symbol, parse_file_selector


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        symbol.suite(),
        parse_file_selector.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
