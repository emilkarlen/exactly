import unittest

from exactly_lib_test.named_element import symbol, file_selector


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        symbol.suite(),
        file_selector.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
