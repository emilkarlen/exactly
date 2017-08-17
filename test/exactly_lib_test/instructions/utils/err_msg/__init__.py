import unittest

from exactly_lib_test.instructions.utils.err_msg import path_description


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(path_description.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
