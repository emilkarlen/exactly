import unittest

from exactly_lib_test.test_resources.value_assertions import value_assertion_test


def suite() -> unittest.TestSuite:
    return value_assertion_test.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
