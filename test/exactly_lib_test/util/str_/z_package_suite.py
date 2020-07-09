import unittest

from exactly_lib_test.util.str_ import name


def suite() -> unittest.TestSuite:
    return name.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
