import unittest

from exactly_lib_test.test_case_utils.line_matcher.test_resources_test import sdv_assertions


def suite() -> unittest.TestSuite:
    return sdv_assertions.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
