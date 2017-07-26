import unittest

from exactly_lib_test.instructions.utils import parse


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(parse.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
