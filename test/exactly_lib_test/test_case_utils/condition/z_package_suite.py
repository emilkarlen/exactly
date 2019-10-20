import unittest

from exactly_lib_test.test_case_utils.condition.integer import z_package_suite as integer


def suite() -> unittest.TestSuite:
    return integer.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
