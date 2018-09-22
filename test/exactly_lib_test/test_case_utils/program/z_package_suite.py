import unittest

from exactly_lib_test.test_case_utils.program.parse import z_package_suite as parse


def suite() -> unittest.TestSuite:
    return parse.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
