import unittest

from exactly_lib_test.value_definition.test_resources_test import concrete_restriction_assertion, \
    concrete_value_assertions_2__file_ref, concrete_value_assertions_2__string, concrete_value_assertions_2, \
    value_structure_assertions, value_reference_assertions, \
    path_relativity, file_ref_relativity


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(path_relativity.suite())
    ret_val.addTest(file_ref_relativity.suite())
    ret_val.addTest(concrete_restriction_assertion.suite())
    ret_val.addTest(concrete_value_assertions_2__string.suite())
    ret_val.addTest(concrete_value_assertions_2__file_ref.suite())
    ret_val.addTest(concrete_value_assertions_2.suite())
    ret_val.addTest(value_structure_assertions.suite())
    ret_val.addTest(value_reference_assertions.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
