import unittest

from exactly_lib_test.test_resources.value_assertions import value_assertion_test


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(value_assertion_test.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
