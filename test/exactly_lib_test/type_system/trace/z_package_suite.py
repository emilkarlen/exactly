import unittest

from exactly_lib_test.type_system.trace.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
