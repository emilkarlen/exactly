import unittest

from exactly_lib_test.symbol.test_resources_test import concrete_value_assertions__file_ref, \
    concrete_value_assertions__string, concrete_value_assertions, \
    value_structure_assertions, symbol_reference_assertions, \
    path_relativity, file_ref_relativity


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(path_relativity.suite())
    ret_val.addTest(file_ref_relativity.suite())
    ret_val.addTest(concrete_value_assertions__string.suite())
    ret_val.addTest(concrete_value_assertions__file_ref.suite())
    ret_val.addTest(concrete_value_assertions.suite())
    ret_val.addTest(value_structure_assertions.suite())
    ret_val.addTest(symbol_reference_assertions.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
