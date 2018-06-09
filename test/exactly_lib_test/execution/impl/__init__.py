import unittest

from exactly_lib_test.execution.impl import symbols_handling


def suite() -> unittest.TestSuite:
    return symbols_handling.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
