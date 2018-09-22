import unittest

from exactly_lib_test.test_case import error_description
from exactly_lib_test.test_case.phases import z_package_suite as phases
from exactly_lib_test.test_case.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(error_description.suite())
    ret_val.addTest(phases.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
