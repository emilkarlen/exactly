import unittest

from exactly_lib_test.symbol.logic import visitor


def suite() -> unittest.TestSuite:
    return visitor.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
