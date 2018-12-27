import unittest

from exactly_lib_test.test_case_utils.string_matcher import resolvers


def suite() -> unittest.TestSuite:
    return resolvers.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
