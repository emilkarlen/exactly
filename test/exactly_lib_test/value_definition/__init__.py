import unittest

from exactly_lib_test.value_definition import test_resources_test
from exactly_lib_test.value_definition import value_structure, concrete_values, concrete_restrictions, value_resolvers


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(value_structure.suite())
    ret_val.addTest(concrete_values.suite())
    ret_val.addTest(concrete_restrictions.suite())
    ret_val.addTest(value_resolvers.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
