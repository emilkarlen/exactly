import unittest

from exactly_lib_test.impls.exception import pfh_exception, svh_exception


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        pfh_exception.suite(),
        svh_exception.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
