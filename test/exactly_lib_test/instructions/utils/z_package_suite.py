import unittest

from exactly_lib_test.instructions.utils.err_msg import z_package_suite as err_msg


def suite() -> unittest.TestSuite:
    return err_msg.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
