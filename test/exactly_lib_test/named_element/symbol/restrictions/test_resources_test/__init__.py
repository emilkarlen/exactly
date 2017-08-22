import unittest

from exactly_lib_test.named_element.symbol.restrictions.test_resources_test import concrete_restriction_assertion


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(concrete_restriction_assertion.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
