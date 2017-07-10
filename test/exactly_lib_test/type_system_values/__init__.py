import unittest

from exactly_lib_test.type_system_values import string_value


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(string_value.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
