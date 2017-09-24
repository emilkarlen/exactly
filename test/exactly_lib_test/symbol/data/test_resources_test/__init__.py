import unittest

from exactly_lib_test.symbol.data.test_resources_test import concrete_value_assertions__file_ref, \
    concrete_value_assertions__string, any_resolver_assertions, \
    symbol_structure_assertions, symbol_reference_assertions, \
    file_ref_relativity, list_assertions
from exactly_lib_test.symbol.data.test_resources_test import path_relativity


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(path_relativity.suite())
    ret_val.addTest(file_ref_relativity.suite())
    ret_val.addTest(concrete_value_assertions__string.suite())
    ret_val.addTest(concrete_value_assertions__file_ref.suite())
    ret_val.addTest(any_resolver_assertions.suite())
    ret_val.addTest(symbol_structure_assertions.suite())
    ret_val.addTest(symbol_reference_assertions.suite())
    ret_val.addTest(list_assertions.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
