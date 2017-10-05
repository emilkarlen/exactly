import unittest

from exactly_lib_test.common import help


def suite() -> unittest.TestSuite:
    return help.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
