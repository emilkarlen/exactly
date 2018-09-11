import unittest

from exactly_lib_test.symbol.data.restrictions import test_resources_test
from exactly_lib_test.symbol.data.restrictions import value_restrictions, reference_restrictions


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(value_restrictions.suite())
    ret_val.addTest(reference_restrictions.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
