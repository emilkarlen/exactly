import unittest

from exactly_lib_test.named_element import file_selector
from exactly_lib_test.named_element import test_resources_test, symbol


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        symbol.suite(),
        file_selector.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
