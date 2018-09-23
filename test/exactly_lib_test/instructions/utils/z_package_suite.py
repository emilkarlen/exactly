import unittest

from exactly_lib_test.instructions.utils import return_svh_via_exceptions
from exactly_lib_test.instructions.utils.err_msg import z_package_suite as err_msg


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(return_svh_via_exceptions.suite())
    ret_val.addTest(err_msg.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())