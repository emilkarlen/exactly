import unittest

from exactly_lib_test.named_element.symbol.restrictions.test_resources_test import concrete_restriction_assertion


def suite() -> unittest.TestSuite:
    return concrete_restriction_assertion.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
