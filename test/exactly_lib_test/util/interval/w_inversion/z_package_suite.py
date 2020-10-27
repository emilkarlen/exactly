import unittest

from exactly_lib_test.util.interval.w_inversion import intervals, combination


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        intervals.suite(),
        combination.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
