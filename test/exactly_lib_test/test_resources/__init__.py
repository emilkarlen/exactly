import unittest

from exactly_lib_test.test_resources import value_assertions_test


def suite() -> unittest.TestSuite:
    return value_assertions_test.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
