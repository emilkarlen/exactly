import unittest

from exactly_lib_test.symbol.data import concrete_resolvers
from exactly_lib_test.symbol.data import string_resolver, list_resolver, string_resolvers, visitor
from exactly_lib_test.symbol.data import symbol_usage
from exactly_lib_test.symbol.data.file_ref_resolver_impls import z_package_suite as file_ref_resolver_impls
from exactly_lib_test.symbol.data.restrictions import z_package_suite as restrictions
from exactly_lib_test.symbol.data.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(visitor.suite())
    ret_val.addTest(restrictions.suite())
    ret_val.addTest(symbol_usage.suite())
    ret_val.addTest(string_resolver.suite())
    ret_val.addTest(list_resolver.suite())
    ret_val.addTest(concrete_resolvers.suite())
    ret_val.addTest(file_ref_resolver_impls.suite())
    ret_val.addTest(string_resolvers.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
