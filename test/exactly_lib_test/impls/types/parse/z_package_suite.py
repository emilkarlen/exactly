import unittest

from exactly_lib_test.impls.types.parse import symbol_syntax, misc_utils, parse_list


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(misc_utils.suite())
    ret_val.addTest(symbol_syntax.suite())
    ret_val.addTest(parse_list.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
