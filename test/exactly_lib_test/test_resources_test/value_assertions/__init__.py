import unittest

from exactly_lib_test.test_resources_test.value_assertions import value_assertion


def suite() -> unittest.TestSuite:
    return value_assertion.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
