import unittest

from exactly_lib_test.type_val_deps.test_resources_test.w_str_rend import value_restrictions_visitor, \
    value_restriction_assertions, any_sdv_assertions, \
    data_restrictions_assertions, symbol_structure_assertions, symbol_reference_assertions


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(value_restrictions_visitor.suite())
    ret_val.addTest(value_restriction_assertions.suite())
    ret_val.addTest(any_sdv_assertions.suite())
    ret_val.addTest(symbol_structure_assertions.suite())
    ret_val.addTest(symbol_reference_assertions.suite())
    ret_val.addTest(data_restrictions_assertions.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
