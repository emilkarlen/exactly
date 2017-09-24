import unittest

from exactly_lib_test.symbol.data import restrictions, test_resources_test, value_resolvers, concrete_resolvers
from exactly_lib_test.symbol.data import string_resolver, list_resolver
from exactly_lib_test.symbol.data import symbol_usage


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(restrictions.suite())
    ret_val.addTest(symbol_usage.suite())
    ret_val.addTest(string_resolver.suite())
    ret_val.addTest(list_resolver.suite())
    ret_val.addTest(concrete_resolvers.suite())
    ret_val.addTest(value_resolvers.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
