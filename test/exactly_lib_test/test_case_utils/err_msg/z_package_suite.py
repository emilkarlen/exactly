import unittest

from exactly_lib_test.test_case_utils.err_msg import path_description


def suite() -> unittest.TestSuite:
    return path_description.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())