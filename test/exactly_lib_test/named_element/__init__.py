import unittest

from exactly_lib_test.named_element import restriction, file_selector, symbol
from exactly_lib_test.named_element import test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        restriction.suite(),
        symbol.suite(),
        file_selector.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
