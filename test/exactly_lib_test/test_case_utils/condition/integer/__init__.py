import unittest

from exactly_lib_test.test_case_utils.condition.integer import integer_resolver, parse


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        integer_resolver.suite(),
        parse.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
