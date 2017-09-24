import unittest

from exactly_lib_test.symbol.data.restrictions.test_resources_test import concrete_restriction_assertion


def suite() -> unittest.TestSuite:
    return concrete_restriction_assertion.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
