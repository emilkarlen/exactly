import unittest

from exactly_lib_test.named_element import symbol


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        symbol.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
