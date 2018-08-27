import unittest

from exactly_lib_test.test_case import error_description
from exactly_lib_test.test_case import phases
from exactly_lib_test.test_case import test_resources_test


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(error_description.suite())
    ret_val.addTest(phases.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
