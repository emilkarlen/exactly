import unittest

from shellcheck_lib_test.test_suite import enumeration, suite_hierarchy_reading, execution


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(enumeration.suite())
    ret_val.addTest(suite_hierarchy_reading.suite())
    ret_val.addTest(execution.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
