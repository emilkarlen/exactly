import unittest

from exactly_lib_test.test_case_utils.matcher import constant


def suite() -> unittest.TestSuite:
    return constant.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
