import unittest

from exactly_lib_test.symbol.data import concrete_sdvs
from exactly_lib_test.symbol.data import string_sdv, list_sdv, string_sdvs, visitor
from exactly_lib_test.symbol.data import symbol_usage
from exactly_lib_test.symbol.data.path_sdv_impls import z_package_suite as path_sdv_impls
from exactly_lib_test.symbol.data.restrictions import z_package_suite as restrictions
from exactly_lib_test.symbol.data.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(visitor.suite())
    ret_val.addTest(restrictions.suite())
    ret_val.addTest(symbol_usage.suite())
    ret_val.addTest(string_sdv.suite())
    ret_val.addTest(list_sdv.suite())
    ret_val.addTest(concrete_sdvs.suite())
    ret_val.addTest(path_sdv_impls.suite())
    ret_val.addTest(string_sdvs.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
