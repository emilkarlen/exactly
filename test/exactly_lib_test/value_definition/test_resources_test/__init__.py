import unittest

from exactly_lib_test.value_definition.test_resources_test import concrete_restriction_assertion, \
    value_structure_assertions
from exactly_lib_test.value_definition.test_resources_test import value_definition, value_reference


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(concrete_restriction_assertion.suite())
    ret_val.addTest(value_structure_assertions.suite())
    ret_val.addTest(value_reference.suite())
    ret_val.addTest(value_definition.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
