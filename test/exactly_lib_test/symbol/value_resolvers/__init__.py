import unittest

from exactly_lib_test.symbol.value_resolvers import file_ref_with_symbol
from exactly_lib_test.symbol.value_resolvers import path_part_resolvers
from exactly_lib_test.symbol.value_resolvers import string_resolvers


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(string_resolvers.suite())
    ret_val.addTest(path_part_resolvers.suite())
    ret_val.addTest(file_ref_with_symbol.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
