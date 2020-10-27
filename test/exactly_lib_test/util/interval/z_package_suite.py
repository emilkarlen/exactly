import unittest

from exactly_lib_test.util.interval import int_interval


def suite() -> unittest.TestSuite:
    return int_interval.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
