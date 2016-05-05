import unittest

from exactly_lib_test.util.cli_syntax.elements import argument


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(argument.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
