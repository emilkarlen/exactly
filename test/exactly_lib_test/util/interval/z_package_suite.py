import unittest

from exactly_lib_test.util.interval import int_interval
from exactly_lib_test.util.interval.w_inversion import z_package_suite as w_inversion


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        int_interval.suite(),
        w_inversion.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
