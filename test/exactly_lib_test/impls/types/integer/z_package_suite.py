import unittest

from exactly_lib_test.impls.types.integer import integer_sdv, parse_integer


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        integer_sdv.suite(),
        parse_integer.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
