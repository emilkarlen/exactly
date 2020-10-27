import unittest

from exactly_lib_test.test_case_utils.interval import matcher_interval


def suite() -> unittest.TestSuite:
    return matcher_interval.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
