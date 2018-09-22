import unittest

from exactly_lib_test.test_case.phases import common


def suite() -> unittest.TestSuite:
    return common.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
