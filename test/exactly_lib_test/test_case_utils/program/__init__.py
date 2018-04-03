import unittest

from exactly_lib_test.test_case_utils.program import parse


def suite() -> unittest.TestSuite:
    return parse.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
