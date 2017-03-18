import unittest

from exactly_lib_test.value_definition.test_resources_test import concrete_restriction_assertion, \
    concrete_value_assertion, value_structure_assertions


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(concrete_restriction_assertion.suite())
    ret_val.addTest(concrete_value_assertion.suite())
    ret_val.addTest(value_structure_assertions.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
