import unittest

from exactly_lib_test.impls.types.interval import matcher_interval


def suite() -> unittest.TestSuite:
    return matcher_interval.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
