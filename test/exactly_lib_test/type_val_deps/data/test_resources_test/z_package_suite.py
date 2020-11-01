import unittest

from exactly_lib_test.type_val_deps.data.test_resources_test import any_sdv_assertions, \
    symbol_structure_assertions
from exactly_lib_test.type_val_deps.data.test_resources_test import symbol_reference_assertions, \
    concrete_restriction_assertion


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(concrete_restriction_assertion.suite())
    ret_val.addTest(any_sdv_assertions.suite())
    ret_val.addTest(symbol_structure_assertions.suite())
    ret_val.addTest(symbol_reference_assertions.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
