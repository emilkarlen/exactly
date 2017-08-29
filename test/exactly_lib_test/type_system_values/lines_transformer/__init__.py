import unittest

from exactly_lib_test.type_system_values.lines_transformer import vistor


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(vistor.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
