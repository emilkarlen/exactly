import unittest

from exactly_lib_test.definitions import concrete_cross_refs


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(concrete_cross_refs.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
