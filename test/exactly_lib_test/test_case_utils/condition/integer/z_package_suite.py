import unittest

from exactly_lib_test.test_case_utils.condition.integer import integer_resolver, parse_integer_condition


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        integer_resolver.suite(),
        parse_integer_condition.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
