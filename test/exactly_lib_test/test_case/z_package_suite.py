import unittest

from exactly_lib_test.test_case import error_description
from exactly_lib_test.test_case.result import z_package_suite as result
from exactly_lib_test.test_case.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(result.suite())
    ret_val.addTest(error_description.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
