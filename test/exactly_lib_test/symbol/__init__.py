import unittest

from exactly_lib_test.symbol import string_resolver
from exactly_lib_test.symbol import symbol_usage, concrete_resolvers, concrete_restrictions, value_resolvers
from exactly_lib_test.symbol import test_resources_test


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(symbol_usage.suite())
    ret_val.addTest(string_resolver.suite())
    ret_val.addTest(concrete_resolvers.suite())
    ret_val.addTest(concrete_restrictions.suite())
    ret_val.addTest(value_resolvers.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
